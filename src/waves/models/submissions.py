""" Each WAVES service allows multiple job 'submissions' """
from __future__ import unicode_literals
from django.core.exceptions import ValidationError
from django.db import models
import logging
from waves.models import TimeStamped, ApiModel, Ordered, Slugged, Service, Described, DTOMixin
from waves.models.base import AdaptorInitParam
from waves.models.managers.submissions import *
logger = logging.getLogger(__name__)
__all__ = ['Submission', 'SubmissionOutput', 'SubmissionExitCode', 'SubmissionRunParam']


class Submission(TimeStamped, ApiModel, Ordered, Slugged):
    """ Represents a service submission parameter set for a service """

    class Meta:
        db_table = 'waves_submission'
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
    label = models.CharField('Submission title', max_length=255, null=True, blank=False)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, null=False, related_name='submissions')

    @property
    def available_online(self):
        """ return whether submission is available online """
        return self.availability == 1 or self.availability == 3

    @property
    def available_api(self):
        """ return whether submission is available for api calls """
        return self.availability >= 2

    @property
    def run_params(self):
        """ Return overriden run params if exists, else service's default """
        if self.sub_run_params is not None:
            runner_params = self.sub_run_params.values_list('name', 'value')
            return dict({name: value for name, value in runner_params})
        return self.service.run_params

    def __str__(self):
        return '[%s|%s]' % (self.label, self.service)

    @property
    def expected_inputs(self):
        """ Retrieve only expected inputs to submit a job """
        return self.all_inputs.filter(required__in=(None, True)).all()

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


class SubmissionOutput(TimeStamped):
    """
    Represents usual service parameters output values (share same attributes with ServiceParameters)
    """

    class Meta:
        db_table = 'waves_submission_output'
        verbose_name = 'Output'
        verbose_name_plural = 'Outputs'
        unique_together = ('name', 'submission')
        ordering = ['-created']

    label = models.CharField('Label', max_length=255, null=True, blank=True, help_text="Label")
    name = models.CharField('Name', max_length=200, null=False, blank=False, help_text='Output file name')
    submission = models.ForeignKey(Submission, related_name='outputs', on_delete=models.CASCADE)
    from_input = models.ForeignKey('BaseParam', null=True, blank=True, related_name='to_outputs',
                                   help_text='Valuated with input')
    ext = models.CharField('File extension', max_length=5, null=False, default=".txt")
    optional = models.BooleanField('May be empty ?', default=False)
    file_pattern = models.CharField('File name / pattern', max_length=100, null=False, blank=False, default="%s",
                                    help_text="Pattern used when dependent on any input '%s'")
    edam_format = models.CharField('Edam format', max_length=255, null=True, blank=True, help_text="Edam format")
    edam_data = models.CharField('Edam data', max_length=255, null=True, blank=True, help_text="Edam data")

    def __str__(self):
        if self.from_input:
            return '"%s" (%s) ' % (self.name, self.file_pattern)
        return '%s' % self.name

    def clean(self):
        cleaned_data = super(SubmissionOutput, self).clean()
        if not self.from_input and self.file_pattern == "%s":
            raise ValidationError('You must set a file name')
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
        db_table = "waves_submission_run_params"
        verbose_name = 'Submission\'s adaptor init param'
        unique_together = ('submission', 'name')

    objects = SubmissionRunParamManager()
    submission = models.ForeignKey(Submission, null=False, related_name='sub_run_params',
                                   on_delete=models.CASCADE, help_text='Submission overrides services run params')
