"""
WAVES Services related models objects
"""
from __future__ import unicode_literals

import logging
import os

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models, transaction
from django.contrib.auth import get_user_model
from django.conf import settings
from mptt.models import MPTTModel, TreeForeignKey

import waves.const
import waves.settings
from waves.models.base import *
from waves.models.managers.services import ServiceCategoryManager, ServiceManager, ServiceRunParamManager
from waves.models.runners import Runner
from waves.models.base import AdaptorInitParam

logger = logging.getLogger(__name__)
__all__ = ['ServiceRunParam', 'ServiceCategory', 'Service', 'ServiceMeta']


class ServiceCategory(MPTTModel, Ordered, Described, ApiModel):
    """ Service category """

    class Meta:
        db_table = 'waves_service_category'
        unique_together = ('api_name',)
        ordering = ['name']
        verbose_name_plural = "Categories"
        verbose_name = "Category"

    class MPTTMeta:
        level_attr = 'mptt_level'
        order_insertion_by = ['name']

    objects = ServiceCategoryManager()
    name = models.CharField('Category Name', null=False, blank=False, max_length=255, help_text='Category name')
    ref = models.URLField('Reference', null=True, blank=True, help_text='Category online reference')
    parent = TreeForeignKey('self', null=True, blank=True, help_text='Parent category',
                            related_name='children_category', db_index=True)

    def __str__(self):
        return self.name


class ServiceRunParam(AdaptorInitParam):
    """ Defined runner param for Service model objects """

    class Meta:
        db_table = 'waves_service_run_param'
        verbose_name = 'Run configuration'
        verbose_name_plural = 'Run configuration'
        unique_together = ('service', 'name')

    objects = ServiceRunParamManager()
    service = models.ForeignKey('Service', null=False, related_name='srv_run_params', on_delete=models.CASCADE)


class Service(TimeStamped, Described, ApiModel, ExportAbleMixin, DTOMixin):
    """
    Represents a service on the platform
    """

    # TODO add version number validation
    # TODO add check for mandatory expected params setup (mandatory with no default, not mandatory with default)
    class Meta:
        ordering = ['name']
        db_table = 'waves_service'
        verbose_name = 'Service'
        unique_together = (('api_name', 'version', 'status'),)

    # manager
    objects = ServiceManager()
    _run_on = None
    __adaptor = None
    # fields
    name = models.CharField('Service name', max_length=255, help_text='Service displayed name')
    version = models.CharField('Current version', max_length=10, null=True, blank=True, default='1.0',
                               help_text='Service displayed version')
    runner = models.ForeignKey(Runner, related_name='runs', null=True, blank=False, on_delete=models.SET_NULL,
                               help_text='Service job runs adapter')
    restricted_client = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='restricted_services', blank=True,
                                               verbose_name='Restricted clients', db_table='waves_service_client',
                                               help_text='By default access is granted to everyone, '
                                                         'you may restrict access here.')
    clazz = models.CharField('Parser class', null=True, blank=True, max_length=255,
                             help_text='Service job submission command')
    category = models.ForeignKey(ServiceCategory, on_delete=models.SET_NULL, null=True, related_name='category_tools',
                                 help_text='Service category')
    status = models.IntegerField(choices=waves.const.SRV_STATUS_LIST, default=waves.const.SRV_DRAFT,
                                 help_text='Service online status')
    api_on = models.BooleanField('Available on API', default=True, help_text='Service is available for api calls')
    web_on = models.BooleanField('Available on WEB', default=True, help_text='Service is available for web front')
    email_on = models.BooleanField('Notify results', default=True,
                                   help_text='This service sends notification email')
    partial = models.BooleanField('Dynamic outputs', default=False,
                                  help_text='Set whether some service outputs are dynamic (not known in advance)')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    remote_service_id = models.CharField('Remote service tool ID', max_length=255, editable=False, null=True)
    edam_topics = models.TextField('Edam topics', null=True, blank=True,
                                   help_text='Comma separated list of Edam ontology topics')
    edam_operations = models.TextField('Edam operations', null=True, blank=True,
                                       help_text='Comma separated list of Edam ontology operations')

    def clean(self):
        cleaned_data = super(Service, self).clean()
        # TODO check changed status with at least one submission available on each submission channel (web/api)
        return cleaned_data

    def __init__(self, *args, **kwargs):
        super(Service, self).__init__(*args, **kwargs)
        self._run_on = self.runner

    @classmethod
    def from_db(cls, db, field_names, values):
        """ Executed each time a Service is restored from DB layer"""
        instance = super(Service, cls).from_db(db, field_names, values)
        instance._run_on = instance.runner
        return instance

    @property
    def has_changed_runner(self):
        """
        Return true whether current object changed its runner related model
        :return: True / False
        """
        return self._run_on != self.runner

    def __str__(self):
        return "%s v(%s)" % (self.name, self.version)

    def reset_run_params(self):
        """
        Reset service runner init params with new default, erase unused params
        :param params:
        :return:
        """
        ServiceRunParam.objects.exclude(name__in=self.runner.adaptor.init_params.keys(), service=self).delete()
        for param in self.runner.runner_run_params.filter(prevent_override=True):
            ServiceRunParam.objects.update_or_create(defaults={'value': param.value,
                                                               'prevent_override': True},
                                                     name=param.name, service=self)

    @property
    def jobs(self):
        """ Get current Service Jobs """
        from waves.models import Job
        return Job.objects.filter(submission__in=self.submissions.all())

    @property
    def run_params(self):
        """
        Return a list of tuples representing current service adaptor init params

        :return: a Dictionary (param_name=param_service_value or runner_param_default if not set
        :rtype: dict
        """
        runner_params = self.srv_run_params.all().values_list('name', 'value')
        return dict({name: value for name, value in runner_params})

    def import_service_params(self):
        """ Try to import service param configuration issued from adaptor

        :return: None
        """
        if not self.runner:
            raise ImportError(u'Unable to import if no adaptor is set')

    @property
    def adaptor(self):
        """ Return current adaptor for Service """
        if self.__adaptor is None:
            if not self.runner:
                return None
            # try load it from clazz name
            from django.utils.module_loading import import_string
            Adaptor = import_string(self.runner.clazz)
            self.__adaptor = Adaptor(init_params=self.run_params)
        return self.__adaptor

    @adaptor.setter
    def adaptor(self, adaptor):
        if adaptor is not None:
            from waves.adaptors.base import BaseAdaptor
            assert (isinstance(adaptor, BaseAdaptor))
            self.__adaptor = adaptor

    @property
    def command(self):
        """ Return command parser for current Service """
        if self.clazz:
            from django.utils.module_loading import import_string
            command_parser = import_string(self.clazz)
            # print "command_parser", command_parser
            return command_parser(service=self)
        else:
            from waves.commands.command import BaseCommand
            # print "command_parser", BaseCommand

            return BaseCommand(service=self)

    def service_submission_inputs(self, submission=None):
        """
        Retrieve all
        :param submission:
        :return: corresponding QuerySet object
        :rtype: QuerySet
        """
        if not submission:
            return self.default_submission.submission_inputs
        return submission.submission_inputs

    @transaction.atomic
    def duplicate(self):
        """ Duplicate  a Service / with inputs / outputs / exit_code / runner params """
        from .serializers.services import ServiceSerializer
        from django.contrib import messages
        serializer = ServiceSerializer()
        data = serializer.to_representation(self)
        srv = self.serializer(data=data)
        if srv.is_valid():
            srv.validated_data['name'] += ' (copy)'
            new_object = srv.save()
        else:
            messages.warning('Object could not be duplicated')
            new_object = self
        return new_object

    @property
    def sample_dir(self):
        """ Return expected sample dir for a Service """
        return os.path.join(waves.settings.WAVES_SAMPLE_DIR, self.api_name)

    @property
    def default_submission(self):
        """ Return Service default submission for web forms """
        try:
            return self.submissions.filter(availability__in=(1, 3)).first()
        except ObjectDoesNotExist:
            return None

    @property
    def default_submission_api(self):
        """ Return Service default submission for api """
        try:
            return self.submissions.filter(availability__gt=2).first()
        except ObjectDoesNotExist:
            return None

    @property
    def submissions_web(self):
        """ Returned submissions available on WEB forms """
        return self.submissions.filter(availability__in=(1, 3))

    @property
    def submissions_api(self):
        """ Returned submissions available on API """
        return self.submissions.filter(availability__gt=2)

    def available_for_user(self, user):
        """ Access rules for submission form according to user
        :param user: Request User
        :return: True or False
        """
        if user.is_anonymous():
            return self.status == waves.const.SRV_PUBLIC
        # RULES to set if user can access submissions
        return (self.status == waves.const.SRV_PUBLIC) or \
               (self.status == waves.const.SRV_DRAFT and self.created_by == user) or \
               (self.status == waves.const.SRV_TEST and user.is_staff) or \
               (self.status == waves.const.SRV_RESTRICTED and (
                   user in self.restricted_client.all() or user.is_staff)) or user.is_superuser

    @property
    def serializer(self):
        from waves.models.serializers.services import ServiceSerializer
        return ServiceSerializer

    @property
    def importer(self):
        return self.runner.importer

    def publishUnPublish(self):
        self.status = waves.const.SRV_DRAFT if waves.const.SRV_PUBLIC else waves.const.SRV_PUBLIC
        self.save()


class ServiceMeta(Ordered, Described):
    """
    Represents all meta information associated with a ATGC service service.
    Ex : website, documentation, download, related paper etc...
    """

    class Meta:
        db_table = 'waves_service_meta'
        verbose_name = 'Information'
        unique_together = ('type', 'title', 'order', 'service')

    type = models.CharField('Meta type', max_length=100, choices=waves.const.SERVICE_META)
    title = models.CharField('Title', max_length=255, blank=True, null=True)
    value = models.CharField('Link', max_length=500, blank=True, null=True)
    is_url = models.BooleanField('Is a url', editable=False, default=False)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='metas')

    def duplicate(self, service):
        self.pk = None
        self.service = service
        self.save()
        return self

    def __str__(self):
        return '%s [%s]' % (self.title, self.type)
