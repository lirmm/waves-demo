""" Each WAVES service allows multiple job 'submissions' """
from __future__ import unicode_literals
from django.core.exceptions import ValidationError
from django.db import models
import logging
from waves.models import TimeStamped, ApiModel, Ordered, Slugged, Service, Described
from waves.models.adaptors import AdaptorInitParam, HasRunnerParamsMixin
from waves.models.runners import Runner

logger = logging.getLogger(__name__)
__all__ = ['Submission', 'SubmissionOutput', 'SubmissionExitCode', 'SubmissionRunParam']


class Submission(TimeStamped, ApiModel, Ordered, Slugged, HasRunnerParamsMixin):
    """ Represents a service submission parameter set for a service """

    class Meta:
        db_table = 'waves_submission'
        verbose_name = 'Submission'
        verbose_name_plural = 'Submissions'
        unique_together = ('service', 'api_name')
        ordering = ('order',)

    field_api_name = 'label'
    availability = models.IntegerField('Availability', default=3,
                                       choices=[(0, "Not Available"),
                                                (1, "Available on web only"),
                                                (2, "Available on api only"),
                                                (3, "Available on both")])
    label = models.CharField('Submission title', max_length=255, null=False, blank=False)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, null=False, related_name='submissions')

    def set_run_params_defaults(self):
        # self.runner.adaptor_params.all().delete()
        super(Submission, self).set_run_params_defaults()

    def get_runner(self):
        if self.runner:
            # print "returned overridden ", self.runner
            return self.runner
        else:
            # print "returned service one"
            return self.service.runner

    @property
    def available_online(self):
        """ return whether submission is available online """
        return self.availability == 1 or self.availability == 3

    @property
    def available_api(self):
        """ return whether submission is available for api calls """
        return self.availability >= 2

    def __str__(self):
        return '[%s|%s]' % (self.label, self.service)

    @property
    def expected_inputs(self):
        """ Retrieve only expected inputs to submit a job """
        return self.submission_inputs.exclude(required=False).all()

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

    @property
    def file_inputs(self):
        """ Only files inputs """
        from .inputs import FileInput
        return self.submission_inputs.instance_of(FileInput).all()

    @property
    def params(self):
        """ Exclude files inputs """
        from .inputs import FileInput
        return self.submission_inputs.not_instance_of(FileInput).all()

    @property
    def required_params(self):
        """ Return only required params """
        return self.submission_inputs.filter(required=True)

    @property
    def submission_samples(self):
        from .inputs import FileInputSample
        return self.submission_inputs.instance_of(FileInputSample).all()

    @property
    def pending_jobs(self):
        """ Get current Service Jobs """
        from waves.models import Job
        return self.service_jobs.filter(status__in=Job.PENDING_STATUS)


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

    label = models.CharField('Label', max_length=255, null=True, blank=False, help_text="Label")
    name = models.CharField('File name', max_length=200, null=False, blank=True, help_text='Output file name')
    submission = models.ForeignKey(Submission, related_name='outputs', on_delete=models.CASCADE)
    from_input = models.ForeignKey('BaseParam', null=True, blank=True, related_name='to_outputs',
                                   help_text='Valuated with input')
    ext = models.CharField('File extension', max_length=5, null=False, default=".txt")
    optional = models.BooleanField('May be empty ?', default=False)
    file_pattern = models.CharField('File name / pattern', max_length=100, blank=True, default="%s",
                                    help_text="Pattern used when dependent on any input '%s'")
    edam_format = models.CharField('Edam format', max_length=255, null=True, blank=True, help_text="Edam format")
    edam_data = models.CharField('Edam data', max_length=255, null=True, blank=True, help_text="Edam data")
    help_text = models.TextField('Content description', null=True, blank=True, )

    def __str__(self):
        if self.from_input:
            return '"%s" (%s) ' % (self.from_input.label, self.file_pattern)
        return '%s' % self.name

    def clean(self):
        cleaned_data = super(SubmissionOutput, self).clean()
        if (not self.from_input and self.file_pattern == "%s") and not self.name:
            raise ValidationError({'file_pattern': 'You must set a file name'})
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
        proxy = True
