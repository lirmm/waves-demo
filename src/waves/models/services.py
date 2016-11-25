"""
WAVES Services related models objects
"""
from __future__ import unicode_literals

import logging
import os
from django import forms
from django.db import models, transaction
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.models import Q
from mptt.models import MPTTModel, TreeForeignKey
from django.utils.html import strip_tags
from smart_selects.db_fields import ChainedForeignKey
import waves.const
import waves.settings
from waves.models.base import *
from waves.models.profiles import WavesProfile
from waves.models.runners import RunnerParam, Runner

logger = logging.getLogger(__name__)
__all__ = ['ServiceInputFormat', 'ServiceRunnerParam', 'ServiceCategory', 'Service', 'ServiceSubmission', 'BaseInput',
           'ServiceInput', 'RelatedInput', 'ServiceExitCode', 'ServiceOutput', 'ServiceOutputFromInputSubmission',
           'ServiceMeta']


class ServiceInputFormat(object):
    """
    ServiceInput format validation
    """

    @staticmethod
    def format_number(number):
        return number

    @staticmethod
    def format_boolean(truevalue, falsevalue):
        return '{}|{}'.format(truevalue, falsevalue)

    @staticmethod
    def format_interval(minimum, maximum):
        return '{}|{}'.format(minimum, maximum)

    @staticmethod
    def format_list(values):
        return os.linesep.join([x.strip(' ') for x in values])

    @staticmethod
    def param_type_from_value(value):
        import re
        param_type = waves.const.OPT_TYPE_SIMPLE
        if not value or value == '':
            return param_type
        try:
            """
            (OPT_TYPE_NONE, 'Not used in job submission'),
            (OPT_TYPE_VALUATED, 'Valuated param (--param_name=value)'),
            (OPT_TYPE_SIMPLE, 'Simple param (-param_name value)'),
            (OPT_TYPE_OPTION, 'Option param (-param_name)'),
            (OPT_TYPE_NAMED_OPTION, 'Option named param (--param_name)'),
            (OPT_TYPE_POSIX, 'Positional param (no name)')
            """
            if re.match('--\w+=\w+', value):
                param_type = waves.const.OPT_TYPE_VALUATED
            elif re.match('-\w+ \w+', value):
                param_type = waves.const.OPT_TYPE_SIMPLE
            elif re.match('-{1}\w{1}', value):
                param_type = waves.const.OPT_TYPE_OPTION
            elif re.match('--{1}\w+', value):
                param_type = waves.const.OPT_TYPE_NAMED_OPTION
            else:
                param_type = waves.const.OPT_TYPE_POSIX
            logger.debug("matched %i ", param_type)
        except Exception as e:
            logger.warn("Exception in regexp %s %s", value, e.message)
        return param_type

    @staticmethod
    def choice_list(value):
        list_choice = []
        if value:
            try:
                for param in value.splitlines(False):
                    if '|' in param:
                        val = param.split('|')
                        list_choice.append((val[1], val[0]))
                    else:
                        list_choice.append((param, param))
            except ValueError as e:
                logger.warn('Error Parsing list values %s - value:%s - param:%s', e.message, value, param)
        return list_choice


class ServiceRunnerParamManager(models.Manager):
    def get_by_natural_key(self, service, param):
        return self.get(service=service, param=param)


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


class ServiceCategoryManager(models.Manager):
    def get_by_natural_key(self, api_name):
        return self.get(api_name=api_name)


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


class ServiceManager(models.Manager):
    """
    Service Model 'objects' Manager
    """

    def get_services(self, user=None, for_api=False):
        """

        :param user: current User
        :param for_api: filter only api enabled, either return only web enabled
        :return: QuerySet for services
        :rtype: QuerySet
        """
        if user is not None and not user.is_anonymous():
            if user.is_superuser:
                queryset = self.all()
            elif user.is_staff:
                # Staff user have access their own Services and to all 'Test / Restricted / Public' made by others
                queryset = self.filter(
                    Q(status=waves.const.SRV_DRAFT, created_by=user.profile) |
                    Q(status__in=(waves.const.SRV_TEST, waves.const.SRV_RESTRICTED, waves.const.SRV_PUBLIC))
                )
            else:
                # Simply registered user have access only to "Public" and configured restricted access
                queryset = self.filter(
                    Q(status=waves.const.SRV_RESTRICTED, restricted_client__in=(user.profile,)) |
                    Q(status=waves.const.SRV_PUBLIC)
                )
        # Non logged in user have only access to public services
        else:
            queryset = self.filter(status=waves.const.SRV_PUBLIC)
        if for_api:
            queryset = queryset.filter(api_on=True)
        else:
            queryset = queryset.filter(web_on=True)
        return queryset

    def get_api_services(self, user=None):
        """ Return all api enabled service to User
        """
        return self.get_services(user, for_api=True)

    def get_web_services(self, user=None):
        """ Return all web enabled services """
        return self.get_services(user)

    def get_by_natural_key(self, api_name, version, status):
        return self.get(api_name=api_name, version=version, status=status)


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
    def adaptor(self, value):
        from waves.adaptors.base import JobRunnerAdaptor
        assert(isinstance(value, JobRunnerAdaptor))
        self.__adaptor = value

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


class SubmissionManager(models.Manager):
    """ Django object manager for submissions """
    def get_by_natural_key(self, api_name, service):
        """ Retrived Submission by natural key """
        return self.get(api_name=api_name, service=service)


class ServiceSubmission(TimeStampable, ApiAble, OrderAble, SlugAble):
    """
       Represents a service submission parameter set for a service
    """
    class Meta:
        db_table = 'waves_service_submission'
        verbose_name = 'Submission'
        verbose_name_plural = 'Submissions'
        unique_together = ('service', 'api_name')
        ordering = ('order',)

    field_api_name = 'label'
    objects = SubmissionManager()
    label = models.CharField('Submission label', max_length=255, null=True)
    available_online = models.BooleanField('Available on Web', default=True)
    available_api = models.BooleanField('Available on API', default=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, null=False, related_name='submissions')

    def duplicate_api_name(self):
        return ServiceSubmission.objects.filter(api_name__startswith=self.api_name, service=self.service)

    def natural_key(self):
        """ Set up natural keys for Submissions """
        return self.api_name, self.service.natural_key()

    def save(self, **kwargs):
        """ Overridden save process to manage defaults submissions"""

        super(ServiceSubmission, self).save(**kwargs)

    def __str__(self):
        return self.label

    @property
    def submitted_service_inputs(self):
        return self.service_inputs.filter(editable=True).all()

    @property
    def only_service_inputs(self):
        return ServiceInput.objects.filter(service=self).order_by('-mandatory', 'order')

    def export_service_inputs(self):
        return ServiceInput.objects.filter(service=self).order_by('order')

    def duplicate(self, service):
        """ Duplicate a submission with all its inputs """
        self.service = service
        init_inputs = self.service_inputs.all()
        self.pk = None
        self.save()
        for init_input in init_inputs:
            self.service_inputs.add(init_input.duplicate(self))
        # raise TypeError("Fake")
        return self


class ServiceInputManager(models.Manager):
    def get_by_natural_key(self, label, name, default, service):
        return self.get(label=label, name=name, default=default, service=service)


class BaseInput(DescribeAble, TimeStampable, OrderAble):
    class Meta:
        unique_together = ('label', 'name', 'default', 'service')
        abstract = True

    # _base_manager = models.Manager()

    label = models.CharField('Label', max_length=100, blank=False, null=False, help_text='Input displayed label')
    name = models.CharField('Name', max_length=50, blank=False, null=False, help_text='Input runner\'s job param name')
    default = models.CharField('Default', max_length=255, null=True, blank=True,
                               help_text='Input runner\'s job param default value')
    type = models.CharField('Control Type', choices=waves.const.IN_TYPE, null=False, default=waves.const.TYPE_TEXT,
                            max_length=15, help_text='Input Form generation/control')
    param_type = models.IntegerField('Parameter Type', choices=waves.const.OPT_TYPE, default=waves.const.OPT_TYPE_POSIX,
                                     help_text='Input type (used in command line)')
    format = models.CharField('Type format', null=True, max_length=500, blank=True,
                              help_text='ONE PER LINE<br/>'
                                        'For File: fileExt...<br/>'
                                        'For List: label|value ..."<br/>'
                                        'For Number(optional]: min|max<br/>'
                                        'For Boolean(optional): labelTrue|LabelFalse')
    mandatory = models.BooleanField('Mandatory', default=False, help_text='Input needs is mandatory')
    multiple = models.BooleanField('Multiple', default=False,
                                   help_text='Input may be multiple - only used with File Inputs')
    editable = models.BooleanField('Submitted by user', default=True,
                                   help_text='Input is used for job submission')
    display = models.CharField('List display type', choices=waves.const.LIST_DISPLAY_TYPE, default='select',
                               max_length=100, null=True, blank=True,
                               help_text='Input list display mode (for type list only)')

    def natural_key(self):
        return self.label, self.name, self.default, self.service.natural_key()

    def save(self, *args, **kwargs):
        if not self.short_description and self.description:
            self.short_description = strip_tags(self.description)
        super(BaseInput, self).save(*args, **kwargs)

    def get_choices(self):
        choice_list = []
        if self.type in (waves.const.TYPE_LIST, waves.const.TYPE_FILE):
            choice_list = ServiceInputFormat.choice_list(self.format)
            return choice_list
        elif self.type == waves.const.TYPE_BOOLEAN:
            return [('True', 'True'), ('False', 'False')]
        return choice_list

    def get_min(self):
        if self.type == waves.const.TYPE_INTEGER or self.type == waves.const.TYPE_FLOAT:
            if self.format:
                min_value = self.format.split('|')
                if min_value[0]:
                    return eval(min_value[0])
            return None
        else:
            return None

    def get_max(self):
        if self.type == waves.const.TYPE_INTEGER or self.type == waves.const.TYPE_FLOAT:
            if self.format:
                max_value = self.format.split('|')
                if max_value[1]:
                    return eval(max_value[1])
            return None
        else:
            return None

    @property
    def eval_default(self):
        if self.type == waves.const.TYPE_BOOLEAN:
            return bool(eval(self.default)) if self.default else False
        return self.default

    def clean(self):
        """ Base clean for all service input

        :return:
        """
        if not (self.display or self.default):
            # param is mandatory
            raise forms.ValidationError(
                'Not displayed parameters must have a default value %s:%s' % (self.name, self.label))
            # TODO add mode base controls

    def duplicate(self, submission):
        self.pk = None
        self.service = submission
        return self


class ServiceInput(BaseInput):
    class Meta:
        verbose_name = 'Base Input parameter'
        db_table = 'waves_service_base_input'
        unique_together = ('name', 'service', 'editable', 'param_type')

    service = models.ForeignKey(ServiceSubmission, related_name='service_inputs', on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if self.type == waves.const.TYPE_LIST:
            if self.display == waves.const.DISPLAY_RADIO:
                self.multiple = False

        super(ServiceInput, self).save(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        super(ServiceInput, self).__init__(*args, **kwargs)
        self.__original_type = self.type

    def __str__(self):
        base_str = '%s (%s)' % (self.label, self.type)
        if self.mandatory:
            base_str += ' - mandatory -'
        return base_str

    # TODO use validators already made (and better made)
    def clean(self):
        """ Form validation when creating service Input (check consistency for list / boolean values / integer
        and float default values

        .. todo::
           use validators already made (and better made)

        :return: None
        """
        if self.type != self.__original_type:
            if self.default:
                # validate default value given according to parameter type
                if self.type == waves.const.TYPE_BOOLEAN:
                    try:
                        bool(eval(self.default))
                    except Exception:
                        raise forms.ValidationError('Default value is not a valid boolean value : False|True')
                elif self.type == waves.const.TYPE_INTEGER:
                    try:
                        int(eval(self.default))
                    except Exception:
                        raise forms.ValidationError('Default value is not a valid int value')
                elif self.type == waves.const.TYPE_FLOAT:
                    try:
                        float(eval(self.default))
                    except Exception:
                        raise forms.ValidationError('Default value is not a valid float value: X.Y')
                elif self.type == waves.const.TYPE_LIST:
                    if not any(e[0] == self.default for e in self.get_choices()):
                        raise forms.ValidationError('Default value is not in possible values')
        super(ServiceInput, self).clean()

    def get_value_for_choice(self, value):
        choices = self.get_choices()
        for (code, choice) in choices:
            if code == value:
                return choice
        return None

    def duplicate(self, submission):
        dependent_inputs = self.dependent_inputs.all()
        super(ServiceInput, self).duplicate(submission)
        self.save()
        for related in dependent_inputs:
            logger.debug('Duplicating %s', related)
            self.dependent_inputs.add(related.duplicate(submission, self))
        return self


class RelatedInput(BaseInput):
    class Meta:
        verbose_name = 'Dependent parameter'
        db_table = 'waves_service_related_input'

    when_value = models.CharField('When condition',
                                  max_length=255,
                                  null=False,
                                  blank=False,
                                  help_text='Input is treated only for this parent value')
    related_to = models.ForeignKey(ServiceInput,
                                   related_name="dependent_inputs",
                                   on_delete=models.CASCADE,
                                   null=False,
                                   help_text='Input is associated to')

    def __str__(self):
        return '%s (%s - %s - issued from %s)' % (self.label, self.name, self.type, self.related_to.name)

    def get_value_for_choice(self, value):
        choices = self.related_to.get_choices()
        for (code, choice) in choices:
            if code == value:
                return choice
        return None

    def duplicate(self, submission, related_to):
        self.pk = None
        self.service = submission
        self.related_to = related_to
        self.save()
        return self


class ServiceExitCode(models.Model):
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


class ServiceOutput(TimeStampable, OrderAble, DescribeAble):
    """
    Represents usual service parameters output values (share same attributes with ServiceParameters)
    """

    class Meta:
        db_table = 'waves_service_output'
        verbose_name = 'Service Output'
        unique_together = ('name', 'service')

    name = models.CharField('Name', max_length=200, null=False, blank=False, help_text='Output displayed name')
    service = models.ForeignKey(Service, related_name='service_outputs', on_delete=models.CASCADE,
                                help_text='Output associated service')
    related_from_input = models.ForeignKey('ServiceOutputFromInputSubmission', null=True, blank=True,
                                           related_name='to_output',
                                           help_text='Output is valued from an input')
    from_input = models.BooleanField(default=False, blank=True, help_text="Is valuated from an input value")
    ext = models.CharField('File extension', max_length=5, null=False, default="txt")
    may_be_empty = models.BooleanField('May be empty', default=True)
    file_pattern = models.CharField('File name', max_length=100, null=True, blank=True,
                                    help_text="Format related input value with '%s' if needed")

    def __str__(self):
        if self.from_input:
            return '"%s" (from input %s) ' % (self.name, self.file_pattern)
        return '%s' % self.name

    def save(self, *args, **kwargs):
        if not self.from_input:
            self.may_be_empty = False
        super(ServiceOutput, self).save(*args, **kwargs)

    def clean(self):
        cleaned_data = super(ServiceOutput, self).clean()
        if not self.from_input and not self.file_pattern:
            raise ValidationError('If output is not issued from input, you must set a file name')
        return cleaned_data

    def duplicate(self, service, related_to):
        self.pk = None
        self.service = service
        self.related_from_input = related_to.duplicate(self)
        self.save()
        return self


class ServiceOutputFromInputSubmission(models.Model):
    class Meta:
        db_table = "waves_service_output_submission"
        verbose_name = 'From Input'
        # TODO see if possible or needed
        # unique_together = ('srv_output', 'from_input')

    srv_output = models.ForeignKey(ServiceOutput, related_name='from_input_submission', on_delete=models.CASCADE)
    submission = models.ForeignKey(ServiceSubmission, related_name='service_outputs', on_delete=models.CASCADE)
    srv_input = ChainedForeignKey(
        ServiceInput,
        chained_field='submission',
        chained_model_field='service',
        auto_choose=True,
        null=True,
        blank=True,
        related_name='to_outputs',
        help_text='Output is valued from an input',
        limit_choices_to=Q(Q(type__in=(waves.const.TYPE_FILE, waves.const.TYPE_TEXT, waves.const.TYPE_LIST)),
                           (Q(mandatory=True) | Q(default__isnull=False)))
    )

    def clean(self):
        super(ServiceOutputFromInputSubmission, self).clean()
        if self.srv_input and not (self.srv_input.mandatory or self.srv_input.default):
            raise ValidationError('Valuated output from non mandatory input with no default is not allowed')

    def duplicate(self, srv_output):
        self.pk = None
        self.save()

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
