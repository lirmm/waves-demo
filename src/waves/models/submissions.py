""" Each WAVES service allows multiple job 'submissions' """
from __future__ import unicode_literals
from django.core.exceptions import ValidationError
from django.db import models
import logging
from waves.models import TimeStampable, ApiAble, OrderAble, SlugAble, Service, DescribeAble, DTOAble
from waves.models.base import AdaptorInitParam
from waves.models.managers.submissions import *
logger = logging.getLogger(__name__)
__all__ = ['Submission', 'SubmissionOutput', 'SubmissionExitCode', 'SubmissionRunParam']


class Submission(TimeStampable, ApiAble, OrderAble, SlugAble):
    """ Represents a service submission parameter set for a service """

    class Meta:
        db_table = 'waves_service_submission'
        verbose_name = 'Submission'
        verbose_name_plural = 'Submissions'
        unique_together = ('service', 'api_name')
        ordering = ('order',)

    field_api_name = 'label'
    objects = SubmissionManager()
    availability = models.IntegerField('Availability', default=3,
                                       choices=[(0, "Not Available"),
                                                (1, "Available on web only"),
                                                (2, "Available on api only"),
                                                (3, "Available on both")])
    label = models.CharField('Submission title', max_length=255, null=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, null=False, related_name='submissions')

    @property
    def available_online(self):
        """ return whether submission is available online """
        return self.availability == 1 or self.availability == 3

    @property
    def available_api(self):
        """ return whether submission is available for api calls """
        return self.availability >= 2

    def duplicate_api_name(self):
        return Submission.objects.filter(api_name__startswith=self.api_name, service=self.service)

    def save(self, **kwargs):
        """ Overridden save process to manage defaults submissions"""
        super(Submission, self).save(**kwargs)

    def __str__(self):
        return '[%s|%s]' % (self.label, self.service)

    @property
    def submitted_submission_inputs(self):
        return self.submission_inputs.filter(editable=True).all()

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


class SubmissionOutput(TimeStampable, OrderAble):
    """
    Represents usual service parameters output values (share same attributes with ServiceParameters)
    """

    class Meta:
        db_table = 'waves_service_output'
        verbose_name = 'Output'
        verbose_name_plural = 'Outputs'
        unique_together = ('name', 'submission')
        ordering = ['order']

    label = models.CharField('Label', max_length=255, null=True, blank=True, help_text="Label")
    name = models.CharField('Name', max_length=200, null=False, blank=False, help_text='Output file name')
    submission = models.ForeignKey(Submission, related_name='outputs', on_delete=models.CASCADE)
    from_input = models.ForeignKey('BaseParam', null=True, blank=True, related_name='to_outputs',
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
    submission = models.ForeignKey(Submission, related_name='exit_codes', on_delete=models.CASCADE)
    is_error = models.BooleanField('Is an Error', default=False, blank=False)

    def __str__(self):
        return '{}:{}...'.format(self.exit_code, self.message[0:20])


class SubmissionRunParam(AdaptorInitParam):
    """ Defined runner param for Service model objects """

    class Meta:
        verbose_name = 'Submission\'s adaptor init param'
        unique_together = ('submission', 'name')

    objects = SubmissionRunParamManager()
    submission = models.ForeignKey(Submission, null=False, related_name='sub_run_params',
                                   on_delete=models.CASCADE, help_text='Runner init param for this service')
