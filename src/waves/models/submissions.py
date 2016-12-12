""" Each WAVES service allows multiple job 'submissions' """
from __future__ import unicode_literals

from django import forms
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils.html import strip_tags
from smart_selects.db_fields import ChainedForeignKey
import waves.const
from waves.models import TimeStampable, ApiAble, OrderAble, SlugAble, Service, DescribeAble
from waves.models.managers.submissions import SubmissionManager
from waves.models.services import logger
from waves.models.storage import waves_storage

__all__ = ['ServiceSubmission', 'ServiceInput', 'ServiceOutput', 'RelatedInput', 'ServiceExitCode',
           'ServiceInputSample', 'ServiceSampleDependentInput']


def service_sample_directory(instance, filename):
    return 'sample/{0}/{1}'.format(instance.service.api_name, filename)


class ServiceSubmission(TimeStampable, ApiAble, OrderAble, SlugAble):
    """ Represents a service submission parameter set for a service
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


class SubmissionInput(DescribeAble, TimeStampable, OrderAble):
    """ A classic submission param to setup a service run """
    class Meta:
        unique_together = ('label', 'name', 'default', 'service')

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
    edam_formats = models.CharField('Edam format(s)', max_length=255, null=True, blank=True,
                                    help_text="comma separated list of supported edam format")
    service = models.ForeignKey(ServiceSubmission, related_name='service_inputs', on_delete=models.CASCADE)
    when_value = models.CharField('When condition',
                                  max_length=255,
                                  null=False,
                                  blank=False,
                                  help_text='Input is treated only for this parent value')
    related_to = models.ForeignKey('waves.SubmissionInput',
                                   related_name="dependents",
                                   on_delete=models.CASCADE,
                                   null=False,
                                   help_text='Input is associated to')
    value = None

    def natural_key(self):
        return self.label, self.name, self.default, self.service.natural_key()

    def save(self, *args, **kwargs):
        if not self.short_description and self.description:
            self.short_description = strip_tags(self.description)
        super(SubmissionInput, self).save(*args, **kwargs)

    def get_choices(self):
        choice_list = []
        if self.type in (waves.const.TYPE_LIST, waves.const.TYPE_FILE):
            list_choice = []
            if self.format:
                try:
                    for param in self.format.splitlines(False):
                        if '|' in param:
                            val = param.split('|')
                            list_choice.append((val[1], val[0]))
                        else:
                            list_choice.append((param, param))
                except ValueError as e:
                    logger.warn('Error Parsing list values %s - value:%s - param:%s', e.message, self.format, param)
            return list_choice
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


class ServiceInput(SubmissionInput):
    class Meta:
        verbose_name = 'Base Input parameter'
        proxy = True

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


class RelatedInput(SubmissionInput):
    class Meta:
        verbose_name = 'Dependent parameter'
        db_table = 'waves_service_related_input'
        proxy = True

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


class ServiceOutput(TimeStampable, OrderAble, DescribeAble):
    """
    Represents usual service parameters output values (share same attributes with ServiceParameters)
    """

    class Meta:
        db_table = 'waves_service_output'
        verbose_name = 'Service Output'
        unique_together = ('name', 'service')

    label = models.CharField('Label', max_length=255, null=True, blank=True, help_text="Label")
    name = models.CharField('Name', max_length=200, null=False, blank=False, help_text='Output file name')
    service = models.ForeignKey(ServiceSubmission, related_name='outputs', on_delete=models.CASCADE,
                                help_text='Output associated service')
    related_from_input = models.ForeignKey(ServiceInput, null=True, blank=True,
                                           related_name='to_output',
                                           help_text='Output is valued from an input')
    ext = models.CharField('File extension', max_length=5, null=False, default="txt")
    may_be_empty = models.BooleanField('May be empty', default=True)
    file_pattern = models.CharField('File name', max_length=100, null=True, blank=True,
                                    help_text="Format related input value with '%s' if needed")
    edam_format = models.CharField('Edam format', max_length=255, null=True, blank=True,
                                   help_text="Output expected Edam format")
    edam_data = models.CharField('Edam data', max_length=255, null=True, blank=True,
                                 help_text="Output expected Edam data")

    @property
    def from_input(self):
        return self.related_from_input is not None

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


class ServiceInputSample(models.Model):
    class Meta:
        ordering = ['name']
        db_table = 'waves_service_sample'
        unique_together = ('name', 'input', 'service')

    name = models.CharField('Name', max_length=200, null=False)
    file = models.FileField('File', upload_to=service_sample_directory, storage=waves_storage)
    input = models.ForeignKey('waves.ServiceInput', on_delete=models.CASCADE, related_name='input_samples',
                              help_text='Associated input')
    service = models.ForeignKey('waves.ServiceSubmission', on_delete=models.CASCADE, related_name='services_sample',
                                null=True)
    dependent_inputs = models.ManyToManyField('waves.ServiceInput', through='waves.ServiceSampleDependentInput',
                                              blank=True)


class ServiceSampleDependentInput(models.Model):
    class Meta:
        db_table = 'waves_sample_dependent_input'

    sample = models.ForeignKey('waves.ServiceInputSample', on_delete=models.CASCADE)
    dependent_input = models.ForeignKey('waves.ServiceInput', on_delete=models.CASCADE)
    set_value = models.CharField('When sample selected, set value to ', max_length=200, null=False, blank=False)

