"""
WAVES Services related models objects
"""
from __future__ import unicode_literals

import logging
import os

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models, transaction
from mptt.models import MPTTModel, TreeForeignKey

import waves.const
import waves.settings
from waves.models.base import *
from waves.models.managers.services import ServiceCategoryManager, ServiceManager
from waves.models.profiles import WavesProfile
from waves.models.runners import RunnerParam, Runner

logger = logging.getLogger(__name__)
__all__ = ['ServiceRunnerParam', 'ServiceCategory', 'Service', 'ServiceExitCode', 'ServiceMeta']


class ServiceRunnerParam(models.Model):
    """
    Defined runner param for Service model objects
    """

    class Meta:
        db_table = 'waves_service_runner_param'
        verbose_name = 'Service\'s adaptor init param'
        unique_together = ('service', 'param')

    service = models.ForeignKey('Service', null=False, related_name='service_run_params', on_delete=models.CASCADE,
                                help_text='Runner init param for this service')
    param = models.ForeignKey(RunnerParam, null=False, on_delete=models.CASCADE, related_name='param_srv',
                              help_text='Initial adaptor param')
    _value = models.CharField('Param value', max_length=255, null=True, blank=True, db_column='value',
                              help_text='Runner init param value for this service')

    def natural_key(self):
        return self.service.natural_key(), self.param.natural_key()

    @property
    def value(self):
        """ Getter for current Service Runner Param, return Runner default if not set """
        return self._value if self._value is not None else self.param.default

    def clean(self):
        """
        Check if value or related runner param has a default
        :return:
        """
        if self.param and not (self._value or self.param.default):
            raise ValidationError({'_value': 'You must set a value'})

    def duplicate(self, service):
        self.pk = None
        self.service = service
        return self


class ServiceCategory(MPTTModel, OrderAble, DescribeAble, ApiAble):
    """
    Categorized services
    """

    class Meta:
        db_table = 'waves_service_category'
        verbose_name = 'Service\'s category'
        verbose_name_plural = 'Services\' categories'
        unique_together = ('api_name',)
        ordering = ['name']

    class MPTTMeta:
        order_insertion_by = ['name']

    objects = ServiceCategoryManager()
    name = models.CharField('Category Name',
                            null=False,
                            blank=False,
                            max_length=255,
                            help_text='Category displayed name')
    ref = models.URLField('Reference',
                          null=True,
                          blank=True,
                          help_text='Category description reference')
    parent = TreeForeignKey('self', null=True, blank=True, help_text='This is parent category',
                            related_name='children_category', db_index=True)

    def natural_key(self):
        return (self.api_name,)

    def __str__(self):
        return self.name


class Service(TimeStampable, DescribeAble, ApiAble, ExportAbleMixin):
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
    run_on = models.ForeignKey(Runner, related_name='runs', null=True, blank=True, on_delete=models.SET_NULL,
                               help_text='Service job runs adapter')
    runner_params = models.ManyToManyField(RunnerParam, through=ServiceRunnerParam, related_name='service_init_params',
                                           help_text='Runner initial parameter')
    restricted_client = models.ManyToManyField(WavesProfile, related_name='restricted_services', blank=True,
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
    email_on = models.BooleanField('Notify results to client', default=True,
                                   help_text='This service sends notification email')
    partial = models.BooleanField('Dynamic outputs', default=False,
                                  help_text='Set whether some service outputs are dynamic (not known in advance)')
    created_by = models.ForeignKey(WavesProfile, on_delete=models.SET_NULL, null=True)
    remote_service_id = models.CharField('Remote service tool ID', max_length=255, editable=False, null=True)
    edam_topics = models.TextField('Edam topics', null=True, help_text='Comma separated list of Edam ontology topics')
    edam_operations = models.TextField('Edam operations', null=True,
                                       help_text='Comma separated list of Edam ontology operations')

    def natural_key(self):
        """ Return natural key for a Service (Django Serializer)"""
        return self.api_name, self.version, self.status

    def __init__(self, *args, **kwargs):
        super(Service, self).__init__(*args, **kwargs)
        self._run_on = self.run_on

    @classmethod
    def from_db(cls, db, field_names, values):
        """ Executed each time a Service is restored from DB layer"""
        instance = super(Service, cls).from_db(db, field_names, values)
        instance._run_on = instance.run_on
        return instance

    @property
    def has_changed_runner(self):
        """
        Return true whether current object changed its runner related model
        :return: True / False
        """
        return self._run_on != self.run_on

    def __str__(self):
        return "%s v(%s)" % (self.name, self.version)

    def reset_default_params(self, params):
        """
        Reset service runner init params with new default, erase unused params
        :param params:
        :return:
        """
        for param in params:
            ServiceRunnerParam.objects.update_or_create(param=param, service=self)

    def run_params(self):
        """
        Return a list of tuples representing current service adaptor init params

        :return: a Dictionary (param_name=param_service_value or runner_param_default if not set
        :rtype: dict
        """
        runner_params = self.service_run_params.all().values_list('param__name', '_value', 'param__default')
        returned = dict()
        for name, value, default in runner_params:
            logger.debug("service run_params %s:%s:%s" % (name, value, default))
            returned[name] = value if value else default
        return returned

    def import_service_params(self):
        """ Try to import service param configuration issued from adaptor

        :return: None
        """
        if not self.run_on:
            raise ImportError(u'Unable to import if no adaptor is set')

    @property
    def adaptor(self):
        """ Return current adaptor for Service """
        if self.__adaptor is None:
            if not self.run_on:
                return None
            # try load it from clazz name
            from django.utils.module_loading import import_string
            Adaptor = import_string(self.run_on.clazz)
            self.__adaptor = Adaptor(init_params=self.run_params())
        return self.__adaptor

    @adaptor.setter
    def adaptor(self, adaptor):
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
            return self.default_submission.service_inputs
        return submission.service_inputs

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
            return self.submissions.filter(available_online=True).first()
        except ObjectDoesNotExist:
            return None

    @property
    def default_submission_api(self):
        """ Return Service default submission for api """
        try:
            return self.submissions.filter(available_api=True).first()
        except ObjectDoesNotExist:
            return None

    @property
    def submissions_web(self):
        """ Returned submissions available on WEB forms """
        return self.submissions.filter(available_online=True)

    @property
    def submissions_api(self):
        """ Returned submissions available on API """
        return self.submissions.filter(available_api=True)

    def available_for_user(self, user):
        """ Access rules for submission form according to user
        :param user: Request User
        :return: True or False
        """
        if user.is_anonymous():
            return self.status == waves.const.SRV_PUBLIC
        # RULES to set if user can access submissions
        return (self.status == waves.const.SRV_PUBLIC) or \
               (self.status == waves.const.SRV_DRAFT and self.created_by == user.profile) or \
               (self.status == waves.const.SRV_TEST and user.is_staff) or \
               (self.status == waves.const.SRV_RESTRICTED and (
                   user.profile in self.restricted_client.all() or user.is_staff)) or user.is_superuser

    @property
    def serializer(self):
        from waves.models.serializers.services import ServiceSerializer
        return ServiceSerializer

    @property
    def importer(self):
        return self.run_on.importer

    def publishUnPublish(self):
        self.status = waves.const.SRV_DRAFT if waves.const.SRV_PUBLIC else waves.const.SRV_PUBLIC
        self.save()


class ServiceExitCode(models.Model):
    """ Services Extended exit code, when non 0/1 usual ones"""
    class Meta:
        db_table = 'waves_service_exitcode'
        verbose_name = 'Service Exit Code'
        unique_together = ('exit_code', 'service')

    exit_code = models.IntegerField('Exit code value')
    message = models.CharField('Exit code message', max_length=255)
    service = models.ForeignKey(Service, related_name='service_exit_codes',
                                on_delete=models.CASCADE)

    def duplicate(self, service):
        self.pk = None
        self.service = service
        return self


class ServiceMeta(OrderAble, DescribeAble):
    """
    Represents all meta information associated with a ATGC service service.
    Ex : website, documentation, download, related paper etc...
    """

    class Meta:
        db_table = 'waves_service_meta'
        verbose_name = 'Service Meta information'
        unique_together = ('type', 'title', 'order', 'service')

    type = models.CharField('Meta type', max_length=100, choices=waves.const.SERVICE_META)
    title = models.CharField('Meta title', max_length=255, blank=True, null=True)
    value = models.CharField('Meta value', max_length=500, blank=True, null=True)
    is_url = models.BooleanField('Is a url', editable=False, default=False)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='metas')

    def duplicate(self, service):
        self.pk = None
        self.service = service
        self.save()
        return self
