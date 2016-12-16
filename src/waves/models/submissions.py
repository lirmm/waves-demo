""" Each WAVES service allows multiple job 'submissions' """
from __future__ import unicode_literals
from django import forms
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.html import strip_tags
import waves.const
import logging
from waves.models import TimeStampable, ApiAble, OrderAble, SlugAble, Service, DescribeAble, DTOAble
from waves.models.runners import AdaptorInitParam
from waves.models.managers.submissions import *

from waves.models.storage import waves_storage

logger = logging.getLogger(__name__)
__all__ = ['ServiceSubmission', 'SubmissionParam', 'FileInput', 'SubmissionOutput', 'RelatedParam',
           'SubmissionExitCode', 'SampleDependentParam', 'SubmissionRunParam', 'SubmissionSample',
           'RelatedFileInput', 'SubmissionData']


def service_sample_directory(instance, filename):
    return 'sample/{0}/{1}'.format(instance.service.api_name, filename)


class ServiceSubmission(TimeStampable, ApiAble, OrderAble, SlugAble):
    """ Represents a service submission parameter set for a service """

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
    def submitted_submission_inputs(self):
        return self.submission_inputs.filter(editable=True).all()

    @property
    def only_submission_inputs(self):
        return SubmissionParam.objects.filter(service=self).order_by('-mandatory', 'order')

    def export_submission_inputs(self):
        return SubmissionParam.objects.filter(service=self).order_by('order')

    def duplicate(self, service):
        """ Duplicate a submission with all its inputs """
        self.service = service
        init_inputs = self.submission_inputs.all()
        self.pk = None
        self.save()
        for init_input in init_inputs:
            self.submission_inputs.add(init_input.duplicate(self))
        # raise TypeError("Fake")
        return self


class SubmissionData(DescribeAble, TimeStampable, OrderAble, DTOAble):
    """ A classic submission param to setup a service run """

    class Meta:
        unique_together = ('name', 'default', 'submission')

    label = models.CharField('Label', max_length=100, blank=False, null=False, help_text='Input displayed label')
    name = models.CharField('Name', max_length=50, blank=False, null=False, help_text='Input runner\'s job param name')
    default = models.CharField('Default', max_length=255, null=True, blank=True)
    type = models.CharField('Control Type', choices=waves.const.IN_TYPE, null=False, default=waves.const.TYPE_TEXT,
                            max_length=15, help_text='Input Form generation/control')
    cmd_line_type = models.IntegerField('Command line type', choices=waves.const.OPT_TYPE,
                                        default=waves.const.OPT_TYPE_POSIX,
                                        help_text='Input type (used in command line)')
    _type_format = models.TextField('Type format', null=True, max_length=500, blank=True)
    required = models.BooleanField('Required', default=False)
    multiple = models.BooleanField('Multiple', default=False)
    submitted = models.BooleanField('Submitted by user', default=True)
    list_display = models.CharField('List display type', choices=waves.const.LIST_DISPLAY_TYPE, default='select',
                                    max_length=100, null=True, blank=True,
                                    help_text='Input list display mode (for type list only)')
    edam_formats = models.CharField('Edam format(s)', max_length=255, null=True, blank=True,
                                    help_text="comma separated list of supported edam format")
    edam_datas = models.CharField('Edam data(s)', max_length=255, null=True, blank=True,
                                  help_text="comma separated list of supported edam data type")
    submission = models.ForeignKey(ServiceSubmission, related_name='submission_inputs', on_delete=models.CASCADE)
    # dedicated to relation ship with other Inputs
    when_value = models.CharField('When condition', max_length=255, null=True, blank=False,
                                  help_text='Input is treated only for this parent value')
    related_to = models.ForeignKey('self', related_name="dependents_inputs", on_delete=models.CASCADE,
                                   null=True, blank=False, help_text='Input is associated to')

    def __str__(self):
        return self.label

    @property
    def format(self):
        return self._type_format

    @format.setter
    def format(self, type_format):
        self._type_format = type_format

    def natural_key(self):
        return self.label, self.name, self.default, self.service.natural_key()

    def save(self, *args, **kwargs):
        if not self.short_description and self.description:
            self.short_description = strip_tags(self.description)
        super(SubmissionData, self).save(*args, **kwargs)

    def get_choices(self, selected=None):
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
        if not (self.list_display or self.default):
            # param is mandatory
            raise forms.ValidationError(
                'Not displayed parameters must have a default value %s:%s' % (self.name, self.label))
            # TODO add mode base controls

    def duplicate(self, submission):
        self.pk = None
        self.service = submission
        return self


class FileInput(SubmissionData):
    """ Service files inputs """

    class Meta:
        proxy = True

    objects = FileInputManager()

    def __init__(self, *args, **kwargs):
        super(FileInput, self).__init__(*args, **kwargs)
        self.type = waves.const.TYPE_FILE


class RelatedFileInput(FileInput):
    class Meta:
        proxy = True

    objects = RelatedFileManager()


class SubmissionParam(SubmissionData):
    """ A Base service input"""

    class Meta:
        proxy = True

    objects = ParamManager()

    def save(self, *args, **kwargs):
        if self.type == waves.const.TYPE_LIST:
            if self.list_display == waves.const.DISPLAY_RADIO:
                self.multiple = False

        super(SubmissionParam, self).save(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        super(SubmissionParam, self).__init__(*args, **kwargs)
        self.__original_type = self.type

    def __str__(self):
        base_str = '%s (%s)' % (self.label, self.type)
        if self.required:
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
        super(SubmissionParam, self).clean()


class RelatedParam(SubmissionParam):
    class Meta:
        proxy = True

    objects = RelatedParamManager()

    def get_choices(self, selected=None):
        return self.related_to.get_choices(selected)


class SubmissionOutput(TimeStampable, OrderAble, DescribeAble):
    """
    Represents usual service parameters output values (share same attributes with ServiceParameters)
    """

    class Meta:
        db_table = 'waves_service_output'
        verbose_name = 'Output'
        verbose_name_plural = 'Outputs'
        unique_together = ('name', 'submission')

    label = models.CharField('Label', max_length=255, null=True, blank=True, help_text="Label")
    name = models.CharField('Name', max_length=200, null=False, blank=False, help_text='Output file name')
    submission = models.ForeignKey(ServiceSubmission, related_name='outputs', on_delete=models.CASCADE)
    from_input = models.ForeignKey(SubmissionData, null=True, blank=True, related_name='to_outputs',
                                   help_text='Valuated with input')
    ext = models.CharField('File extension', max_length=5, null=False, default=".txt")
    optional = models.BooleanField('Optional', default=False)
    file_pattern = models.CharField('File name', max_length=100, null=True, blank=True, default="%s",
                                    help_text="Format pattern '%s'")
    edam_format = models.CharField('Edam format', max_length=255, null=True, blank=True, help_text="Edam format")
    edam_data = models.CharField('Edam data', max_length=255, null=True, blank=True, help_text="Edam data")

    def __str__(self):
        if self.from_input:
            return '"%s" (%s) ' % (self.name, self.file_pattern)
        return '%s' % self.name

    def save(self, *args, **kwargs):
        if not self.from_input:
            self.optional = False
        super(SubmissionOutput, self).save(*args, **kwargs)

    def clean(self):
        cleaned_data = super(SubmissionOutput, self).clean()
        if not self.from_input and not self.file_pattern:
            raise ValidationError('If output is not issued from input, you must set a file name')
        return cleaned_data


class SubmissionExitCode(models.Model):
    """ Services Extended exit code, when non 0/1 usual ones"""

    class Meta:
        db_table = 'waves_service_exitcode'
        verbose_name = 'Exit Code'
        unique_together = ('exit_code', 'submission')

    exit_code = models.IntegerField('Exit code value')
    message = models.CharField('Exit code message', max_length=255)
    submission = models.ForeignKey(ServiceSubmission, related_name='exit_codes', on_delete=models.CASCADE)
    is_error = models.BooleanField('Is an Error', default=False, blank=False)

    def __str__(self):
        return '{}:{}...'.format(self.exit_code, self.message[0:20])


class SubmissionSample(models.Model):
    param = models.ForeignKey(FileInput, null=False, on_delete=models.CASCADE, blank=True, related_name='input_sample')
    sample = models.FileField('File', upload_to=service_sample_directory, storage=waves_storage, blank=True)
    label = models.CharField('Label', max_length=255, blank=True, null=False)
    dependent_params = models.ManyToManyField('waves.SubmissionParam', blank=True, through='waves.SampleDependentParam')


class SampleDependentParam(models.Model):
    """ When a file sample is selected, some params may be set accordingly. This class represent this behaviour"""

    class Meta:
        db_table = 'waves_sample_dependent_input'

    submission_sample = models.ForeignKey(SubmissionSample, on_delete=models.CASCADE, related_name='sp_dep_samples')
    dependent_input = models.ForeignKey(SubmissionParam, on_delete=models.CASCADE, related_name='sp_dep_params')
    value = models.CharField('Set value to ', max_length=200, null=False, blank=False)


class SubmissionRunParam(AdaptorInitParam):
    """ Defined runner param for Service model objects """

    class Meta:
        verbose_name = 'Submission\'s adaptor init param'
        unique_together = ('submission', 'name')

    objects = SubmissionRunParamManager()
    submission = models.ForeignKey(ServiceSubmission, null=False, related_name='sub_run_params',
                                   on_delete=models.CASCADE, help_text='Runner init param for this service')
