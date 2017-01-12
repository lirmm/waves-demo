""" All Input related models """
from __future__ import unicode_literals

from django.core.exceptions import ValidationError
from django.db import models
from polymorphic.models import PolymorphicModel

import waves.const
from waves.models.base import Ordered, DTOMixin
from waves.models.submissions import Submission
from waves.utils.storage import waves_storage, file_sample_directory
from waves.utils.validators import validate_list_comma, validate_list_param

__all__ = ['BaseParam', 'RepeatedGroup', 'FileInput', 'BooleanParam', 'DecimalParam',
           'ListParam', 'SampleDepParam', 'FileInputSample', 'TextParam', 'RelatedParam', 'IntegerParam']


class RepeatedGroup(DTOMixin, Ordered):
    """ Some input may be grouped, and group could be repeated"""

    class Meta:
        db_table = "waves_repeat_group"

    submission = models.ForeignKey(Submission, related_name='submission_groups', null=True,
                                   on_delete=models.CASCADE)
    name = models.CharField('Group name', max_length=255, null=False, blank=False)
    title = models.CharField('Group title', max_length=255, null=False, blank=False)
    max_repeat = models.IntegerField("Max repeat", null=True, blank=True)
    min_repeat = models.IntegerField('Min repeat', default=0)
    default = models.IntegerField('Default repeat', default=0)

    def __str__(self):
        return '[%s]' % (self.name)


class BaseParam(PolymorphicModel):
    """ Base class for services submission params """
    class Meta:
        ordering = ['order']
        unique_together = ('name', 'default', 'submission')
        # base_manager_name = 'base_objects'
        verbose_name = "Submission param"
        verbose_name_plural = "Submission params"

    #: Input Label
    label = models.CharField('Label', max_length=100, blank=False, null=False, help_text='Input displayed label')
    #: Input submission name
    name = models.CharField('Name', max_length=50, blank=False, null=False, help_text='Input runner\'s job param name')
    # TODO validate name with no space
    #: Input default value
    default = models.CharField('Default value', max_length=50, null=True, blank=True)
    #: Input Type
    cmd_format = models.IntegerField('Command line format', choices=waves.const.OPT_TYPE,
                                     default=waves.const.OPT_TYPE_POSIX,
                                     help_text='Command line pattern')
    required = models.NullBooleanField('Required', choices={(None, "Optional"), (True, "Required"),
                                                            (False, "Not submitted")},
                                       default=True, help_text="Submitted and/or Required")
    multiple = models.BooleanField('Multiple', default=False, help_text="Can hold multiple values")
    # TODO remote multiple from base class, only needed for list / file inputs
    help_text = models.TextField('Help Text', null=True, blank=True)
    repeat_group = models.ForeignKey(RepeatedGroup, null=True, blank=True, on_delete=models.SET_NULL,
                                     help_text="Group and repeat items")
    # __future__ :-) manage validators according to edam infos
    #: positive integer field (default to 0)
    order = models.PositiveIntegerField(default=0)
    edam_formats = models.CharField('Edam format(s)', max_length=255, null=True, blank=True,
                                    help_text="comma separated list of supported edam format")
    edam_datas = models.CharField('Edam data(s)', max_length=255, null=True, blank=True,
                                  help_text="comma separated list of supported edam data type")
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, null=False, related_name='submission_inputs')
    # Dedicated Fields for Dependent Inputs
    when_value = models.CharField('When value', max_length=255, null=True, blank=True,
                                  help_text='Input is treated only for this parent value')
    related_to = models.ForeignKey('self', related_name="dependents_inputs", on_delete=models.CASCADE,
                                   null=True, blank=True, help_text='Input is associated to')

    """ Main class for Basic data related to Service submissions inputs """
    class_label = "Basic"

    @property
    def param_type(self):
        return waves.const.TYPE_TEXT

    def save(self, *args, **kwargs):
        if self.repeat_group is not None:
            self.multiple = True
        super(BaseParam, self).save(*args, **kwargs)

    def clean(self):
        if self.required is None and not self.default:
            # param is mandatory
            raise ValidationError('Not displayed parameters must have a default value %s:%s' % (self.name, self.label))
            # TODO add mode base controls

    def __str__(self):
        return self.name


class TextParam(BaseParam):
    """ Standard text input """
    class Meta:
        proxy = True
    class_label = "Text input"




class BooleanParam(BaseParam):
    """ Boolean param (usually check box for a submission option)"""
    class_label = "Boolean"
    true_value = models.CharField('True value', default='True', max_length=50)
    false_value = models.CharField('False value', default='False', max_length=50)

    @property
    def param_type(self):
        return waves.const.TYPE_BOOLEAN


class DecimalParam(BaseParam):
    """ Number param (decimal or float) """
    # TODO add specific validator
    class_label = "Number"
    min_val = models.DecimalField('Min value', decimal_places=3, max_digits=50, default=None, null=True, blank=True,
                                  help_text="Leave blank if no min")
    max_val = models.DecimalField('Max value', decimal_places=3, max_digits=50, default=None, null=True, blank=True,
                                  help_text="Leave blank if no max")

    @property
    def param_type(self):
        return waves.const.TYPE_DECIMAL


class IntegerParam(BaseParam):
    """ Integer param """
    # TODO add specific validator
    class_label = "Integer"
    min_val = models.IntegerField('Min value', default=0, null=True, blank=True,
                                  help_text="Leave blank if no min")
    max_val = models.IntegerField('Max value', default=None, null=True, blank=True,
                                  help_text="Leave blank if no max")

    @property
    def param_type(self):
        return waves.const.TYPE_INT


class RelatedParam(BaseParam):
    """ Proxy class for related params (dependents on other params) """
    class Meta:
        proxy = True


class ListParam(BaseParam):
    """ Param to be issued from a list of values (select / radio / check) """
    class_label = "List"
    list_mode = models.CharField('List display mode', choices=waves.const.LIST_DISPLAY_TYPE, default='select',
                                 max_length=100)
    list_elements = models.TextField('Elements', max_length=500, validators=[validate_list_param, ],
                                     help_text="One Element per line label|value")

    def save(self, *args, **kwargs):
        if self.list_mode == waves.const.DISPLAY_CHECKBOX:
            self.multiple = True
        super(ListParam, self).save(*args, **kwargs)

    def clean(self):
        super(ListParam, self).clean()
        if self.list_mode == waves.const.DISPLAY_RADIO and self.multiple:
            raise ValidationError('You can\'t use radio with multiple choices available')
        elif self.list_mode == waves.const.DISPLAY_CHECKBOX and not self.multiple:
            raise ValidationError('You can\'t use checkboxes with non multiple choices enabled')

    @property
    def choices(self):
        try:
            return list([(line.split('|')[1], line.split('|')[0]) for line in self.list_elements.splitlines()])
        except ValueError:
            raise RuntimeError('Wrong list element format')

    @property
    def param_type(self):
        return waves.const.TYPE_LIST


class FileInput(BaseParam):
    """ Submission file inputs """
    class Meta:
        db_table = 'waves_service_file'
        ordering = ['order', ]
    class_label = "File Input"

    max_size = models.BigIntegerField('Maximum allowed file size ', default=None,  help_text="in Ko")
    allowed_extensions = models.CharField('Filter by extensions', max_length=255,
                                          help_text="Comma separated list, * means no filter",
                                          default="*",
                                          validators=[validate_list_comma, ])

    def __str__(self):
        return self.label

    @property
    def param_type(self):
        return waves.const.TYPE_FILE


class FileInputSample(Ordered):
    """ Any file input can provide samples """
    file = models.FileField('Sample file', upload_to=file_sample_directory, storage=waves_storage, blank=False,
                            null=False)
    file_label = models.CharField('Sample file label', max_length=200, blank=True, null=True)
    file_input = models.ForeignKey(FileInput, on_delete=models.CASCADE, related_name='input_samples')
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='submission_samples')
    dependent_params = models.ManyToManyField(BaseParam, blank=True, through='SampleDepParam')

    @property
    def label(self):
        """ Label for displayed file """
        return self.file_label if self.file_label else self.file.name


class SampleDepParam(models.Model):
    """ When a file sample is selected, some params may be set accordingly. This class represent this behaviour"""

    class Meta:
        db_table = 'waves_sample_dependent_input'

    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='sample_dependent_params')
    sample = models.ForeignKey(FileInputSample, on_delete=models.CASCADE, related_name='dependent_inputs')
    related_to = models.ForeignKey(BaseParam, on_delete=models.CASCADE, related_name='related_samples')
    set_default = models.CharField('Set value to ', max_length=200, null=False, blank=False)
