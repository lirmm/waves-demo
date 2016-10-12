from __future__ import unicode_literals
import os
import logging
import eav
from collections import namedtuple
from django.conf import settings
from django.contrib.auth.models import Group
from django.db import models
from django.db.models import Q
from django.utils.html import format_html
from django.core.exceptions import ValidationError
import waves.const
from waves.exceptions import WavesException
from waves.eav.config import JobEavConfig, JobInputEavConfig, JobOutputEavConfig
from waves.models import TimeStampable, SlugAble, OrderAble, UrlMixin
import waves.settings

__license__ = "MIT"
__revision__ = " $Id: actor.py 1586 2009-01-30 15:56:25Z cokelaer $ "
__docformat__ = 'reStructuredText'

logger = logging.getLogger(__name__)

RunJobInfo = namedtuple("RunJobInfo",
                        """jobId hasExited hasSignal terminatedSignal hasCoreDump
                           wasAborted exitStatus resourceUsage""")

__all__ = ['allow_display_online', 'Job', 'JobInput', 'JobOutput', 'JobHistory', 'JobAdminHistory',
           'JobAdminHistoryManager']


def allow_display_online(file_name):
    """
    Determine if current 'input' or 'output' may be displayed online, maximum file size is set to '1Mo'
    :param file_name: file name to test for size
    :return: bool
    """
    display_file_online = 1024 * 1024 * 1
    try:
        return os.path.getsize(file_name) <= display_file_online
    except os.error:
        return False
    return False


class JobManager(models.Manager):
    """ Job Manager add few shortcut function to default Django models objects Manager
    """

    def get_all_jobs(self):
        """
        Return all jobs currently registered in database, as list of dictionary elements
        :return: QuerySet
        """
        return self.all().values()

    def get_user_job(self, user):
        """
        Filter jobs according to user (logged in) according to following access rule:
        * User is a super_user, return all jobs
        * User is member of staff (access to Django admin): returns only jobs from services user has created,
        jobs created by user, or where associated email is its email
        * User is simply registered on website, returns only those created by its own
        :param user: current user (may be Anonymous)
        :return: QuerySet
        """
        if user.is_superuser:
            return self.all()
        if user.is_staff:
            return self.filter(Q(service__created_by=user) | Q(client=user) | Q(email_to=user.email))
        # return self.filter(Q(client=user) | Q(email_to=user.email))
        return self.filter(client=user)

    def get_service_job(self, user, service):
        """
        Returns jobs filtered by service, according to following access rule:
        * user is simply registered, return its jobs, filtered by service
        :param user: currently logged in user
        :param service: service model object to filter
        :return: QuerySet
        """
        if user.is_superuser or user.is_staff:
            return self.filter(service=service)
        return self.filter(client=user, service=service)

    def get_pending_jobs(self, user=None):
        """
        Return pending jobs for user, according to following access rule:
        * user is simply registered, return its jobs, filtered by service
        :param user: currently logged in user
        :return: QuerySet

        .. note::
            Pending jobs are all jobs which are 'Created', 'Prepared', 'Queued', 'Running'
        """
        if user is not None:
            if user.is_superuser or user.is_staff:
                # return all pending jobs
                return self.filter(status__in=(
                    waves.const.JOB_CREATED, waves.const.JOB_PREPARED, waves.const.JOB_QUEUED,
                    waves.const.JOB_RUNNING))
            # get only user jobs
            return self.filter(status__in=(waves.const.JOB_CREATED, waves.const.JOB_PREPARED,
                                           waves.const.JOB_QUEUED, waves.const.JOB_RUNNING),
                               client=user)
        # User is not supposed to be None
        return self.none()

    def get_created_job(self, extra_filter, user=None):
        """
        Return pending jobs for user, according to following access rule:
        * user is simply registered, return its jobs, filtered by service
        :param extra_filter: add an extra filter to queryset
        :param user: currently logged in user
        :return: QuerySet
        """
        if user is not None:
            self.filter(status=waves.const.JOB_CREATED,
                        client=user,
                        **extra_filter).order_by('-created')
        return self.filter(status=waves.const.JOB_CREATED, **extra_filter).order_by('-created').all()


class Job(TimeStampable, SlugAble, UrlMixin):
    """
    A job represent a request for executing a service, it requires values from specified required input from related
    service
    """
    # non persistent field, used for history savings see signals
    #: Current message associated with job object, not directly stored in job table, but in history
    message = None
    #: Job status issued from last retrieve on DB
    _status = None
    #: Job status time (for history)
    status_time = None
    #: Job run details retrieved or not
    _run_details = None

    class Meta(TimeStampable.Meta):
        db_table = 'waves_job'
        verbose_name = 'Job'
        unique_together = (('service', 'slug'),)

    objects = JobManager()
    #: Job Title, automatic or set by user upon submission
    title = models.CharField('Job title', max_length=255, null=True, blank=True)
    #: Job related Service - see :ref:`service-label`.
    service = models.ForeignKey('Service', related_name='service_jobs', null=False, on_delete=models.CASCADE)
    #: Job last known status - see :ref:`waves-const-label`.
    status = models.IntegerField('Job status', choices=waves.const.STATUS_LIST, default=waves.const.JOB_CREATED,
                                 help_text='Job current run status')
    #: Job last status for which we sent a notification email
    status_mail = models.IntegerField(editable=False, default=9999)
    #: Job associated client, may be null for anonymous submission
    client = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE,
                               related_name='clients_job', help_text='Associated registered user')
    #: Email to notify job status to
    email_to = models.EmailField('Email results', null=True, blank=True,
                                 help_text='Notify results to this email')
    #: Job ExitCode (mainly for admin purpose)
    exit_code = models.IntegerField('Job system exit code', null=False, default=0,
                                    help_text="Job exit code on relative adaptor")
    #: Tell whether job results files are available for download from client
    results_available = models.BooleanField('Results are available', default=False, editable=False)
    #: Jobs are remotely executed, store the remote job id
    remote_job_id = models.CharField('Remote Job ID (on adaptor)', max_length=255, editable=False, null=True)
    #: Job last status retry count (max before Error set in conf)
    nb_retry = models.IntegerField('Nb Retry', editable=False, default=0)

    def __init__(self, *args, **kwargs):
        super(Job, self).__init__(*args, **kwargs)
        self._status = self.status

    def colored_status(self):
        """
        Format a row depending on current Job Status
        :return: Html unicode string
        """
        return format_html('<span class="{}">{}</span>',
                           self.label_class,
                           self.get_status_display())

    def save(self, *args, **kwargs):
        super(Job, self).save(*args, **kwargs)
        self._status = self.status

    def make_job_dirs(self):
        """
        Create job working dirs
        :return: None
        """
        if not os.path.isdir(self.input_dir):
            os.makedirs(self.input_dir, mode=0775)
        if not os.path.isdir(self.output_dir):
            os.makedirs(self.output_dir, mode=0775)
        os.chmod(self.working_dir, 0775)
        os.chmod(self.input_dir, 0775)
        os.chmod(self.output_dir, 0775)
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Job working dir %s (created %s)", self.working_dir, os.path.exists(self.working_dir))
            logger.debug("Job input dir %s (created %s)", self.input_dir, os.path.exists(self.working_dir))
            logger.debug('Job output dir %s (created %s)', self.output_dir, os.path.exists(self.working_dir))

    def delete_job_dirs(self):
        """Upon job deletion in database, cleanup associated working dirs
        :return: None
        """
        import shutil
        shutil.rmtree(self.working_dir, ignore_errors=True)

    @classmethod
    def from_db(cls, db, field_names, values):
        instance = super(Job, cls).from_db(db, field_names, values)
        instance._status = instance.status
        return instance

    def has_changed_status(self):
        """ Tells whether loaded object status is different from the one issued from last retrieve in db

        :return: True if changed, False either
        :rtype: bool
        """
        return self._status != self.status

    @property
    def input_files(self):
        """
        Get files inputs for this jobs

        :return: list of JobInput models instance
        :rtype: QuerySet
        """
        return self.job_inputs.filter(srv_input__type=waves.const.TYPE_FILE)

    @property
    def output_files_exists(self):
        """
        Check if expected outputs are present on disk, return only those ones

        :return: list of file path
        :rtype: list
        """
        all_files = self.job_outputs.all()
        existing = []
        for _file in all_files:
            if os.path.isfile(_file.file_path) and os.path.getsize(_file.file_path) > 0:
                existing.append(_file)
        return existing

    @property
    def output_files(self):
        """
        Return list of all outputs files, whether they exist or not on disk

        .. note::
            Use :func:`output_files_exists` for only existing outputs instead

        :return: a list of JobOuput objects
        :rtype: list
        """
        all_files = self.job_outputs.all()
        return all_files

    @property
    def input_params(self):
        """
        Return all non-file job inputs, i.e job execution parameters

        :return: list of `JobInput` models instance
        :rtype: QuerySet
        """
        return self.job_inputs.exclude(srv_input__type=waves.const.TYPE_FILE)

    @property
    def input_dir(self):
        """
        Current input (files) directory location on disk

        :return: working_dir
        :rtype: unicode
        """
        return self.working_dir

    @property
    def output_dir(self):
        """
        Current outputs (files) directory location on disk

        :return: working_dir
        :rtype: unicode
        """
        return self.working_dir

    @property
    def working_dir(self):
        """Base job working dir

        :return: working dir
        :rtype: unicode
        """
        return os.path.join(settings.WAVES_JOB_DIR, str(self.slug))

    @property
    def adaptor(self):
        """Return current related service adaptor effective class

        :return: a child class of `JobRunnerAdaptor`
        :rtype: `waves.adaptors.runner.JobRunnerAdaptor`
        """
        return self.service.adaptor

    def __str__(self):
        return '[%s][%s]' % (self.slug, self.service.api_name)

    @property
    def command(self):
        """Return current related service command effective class

        :return: a BaseCommand object (or one of its child)
        :rtype: `BaseCommand`
        """
        return self.service.command

    @property
    def command_line(self):
        """Generate full command line for Job

        :return: string representation of command line
        :rtype: unicode
        """
        return self.command.create_command_line(job_inputs=self.job_inputs.all())

    @property
    def label_class(self):
        """Return css class label associated with current Job Status

        :return: a css class (based on bootstrap)
        :rtype: unicode
        """
        if self.status in (waves.const.JOB_UNDEFINED, waves.const.JOB_SUSPENDED):
            return 'warning'
        elif self.status == waves.const.JOB_ERROR:
            return 'danger'
        elif self.status == waves.const.JOB_CANCELLED:
            return 'info'
        else:
            return 'success'

    def check_send_mail(self):
        """According to job status, check needs for sending notification emails

        :return: the nmmber of mail sent (should be one)
        :rtype: int
        """
        from waves.managers.mails import JobMailer
        if waves.settings.WAVES_NOTIFY_RESULTS and self.service.email_on:
            if self.email_to is not None and self.status != self.status_mail:
                # should send a email
                try:
                    nb_sent = 0
                    mailer = JobMailer(job=self)
                    if self.status == waves.const.JOB_CREATED:
                        nb_sent = mailer.send_job_submission_mail()
                    elif self.status == waves.const.JOB_TERMINATED:
                        nb_sent = mailer.send_job_completed_mail()
                    elif self.status == waves.const.JOB_ERROR:
                        nb_sent = mailer.send_job_error_email()
                    elif self.status == waves.const.JOB_CANCELLED:
                        nb_sent = mailer.send_job_cancel_email()
                    # Avoid resending emails when last status mail already sent
                    self.status_mail = self.status
                    if nb_sent:
                        self.job_history.add(JobAdminHistory.objects.create(message='Sent notification email',
                                                                            status=self.status,
                                                                            job=self))
                    self.save()
                    return nb_sent
                except Exception as e:
                    logger.error('Unable to send mail : %s', e.message)
                    if settings.DEBUG:
                        raise e

    def get_absolute_url(self):
        """Reverse url for this Job according to Django urls configuration

        :return: the absolute uri of this job (without host)
        """
        from django.core.urlresolvers import reverse
        return reverse('waves:job_details', kwargs={'slug': self.slug})

    @property
    def link(self):
        """ short cut to :func:`get_url()`

        :return: current absolute uri for Job
        """
        return self.get_url()

    @property
    def details_available(self):
        """Check whether run details are available for this JOB

        .. note::
            Not really yet implemented

        :return: True is exists, False either
        :rtype: bool
        """
        return os.path.isfile(os.path.join(self.working_dir, 'run_details.p'))

    def load_run_details(self):
        """Return a `RunJobInfo` object associated with this job run

        .. note::
            Not really yet implemented

        :return: the jobInfo
        :rtype: `RunjobInfo`
        """
        job_info = RunJobInfo()
        if self.details_available:
            import pickle
            try:
                with open(os.path.join(self.working_dir, 'run_details.p')) as fp:
                    job_info = pickle.load(fp)
            except pickle.PickleError as e:
                logger.warn('Unable to load JobRunInfo [job:%s]', self.slug)
        return job_info

    @property
    def stdout(self):
        """ Hard coded job standard output file name

        :rtype: unicode
        """
        return 'job.stdout'

    @property
    def stderr(self):
        """ Hard coded job standard error file name

        :rtype: unicode
        """
        return 'job.stderr'

    def create_non_editable_inputs(self, service_submission):
        """ Create non editable (i.e not submitted anywhere and used for run)

        .. seealso::
            Used in post_save signals

        :param service_submission:
        :return: None
        """
        for service_input in service_submission.service_inputs.filter(editable=False) \
                .exclude(param_type=waves.const.OPT_TYPE_NONE):
            # Create fake "submitted_inputs" with non editable ones with default value if not already set
            logger.debug('Created non editable job input: %s (%s, %s)', service_input.label,
                         service_input.name, service_input.default)
            self.job_inputs.add(JobInput.objects.create(job=self, srv_input=service_input,
                                                        order=service_input.order,
                                                        value=service_input.default))

    def create_default_outputs(self):
        """ Create standard default outputs for job (stdout and stderr)

        :return: None
        """
        output_dict = dict(job=self, value='job.stdout', may_be_empty=True, srv_output=None)
        out = JobOutput.objects.create(**output_dict)
        self.job_outputs.add(out)
        output_dict['value'] = 'job.stderr'
        out1 = JobOutput.objects.create(**output_dict)
        self.job_outputs.add(out1)
        logger.debug('Created default outputs: [%s, %s]', out, out1)

    @property
    def public_history(self):
        """Filter Job history elements for public (non `JobAdminHistory` elements)

        :rtype: QuerySet
        """
        return self.job_history.filter(is_admin=False)

    def cancel_job(self, admin=False):
        self.status = waves.const.JOB_CANCELLED
        try:
            self.adaptor.cancel_job(self)
        except WavesException as exc:
            from waves.models.jobs import JobAdminHistory
            JobAdminHistory.objects.create(job=self, status=self.status,
                                           message="Unable to remotely cancel job, %s" % exc.message)
        self.message = "Job automatically cancelled"
        if admin:
            self.message += " (by admin)"
        self.save()


class JobInput(OrderAble, SlugAble):
    """
    Job Inputs is association between a Job, a ServiceInput, setting a value specific for this job
    """
    class Meta:
        db_table = 'waves_job_input'
        unique_together = ('srv_input', 'job', 'value')

    #: Reference to related :class:`waves.models.jobs.Job`
    job = models.ForeignKey(Job, related_name='job_inputs', on_delete=models.CASCADE)
    #: Reference to related :class:`waves.models.services.ServiceInput`
    srv_input = models.ForeignKey('BaseInput', null=True, on_delete=models.CASCADE)
    #: Value set to this service input for this job
    value = models.CharField('Input content', max_length=255, null=True, blank=True,
                             help_text='Input value (filename, boolean value, int value etc.)')

    def __str__(self):
        return u'|'.join([self.name, str(self.value)])

    @property
    def param_type(self):
        """ Current input type

        :return: one of const types defined for ServiceInput
        """
        return self.srv_input.param_type if self.srv_input else waves.const.OPT_TYPE_POSIX

    @property
    def name(self):
        """ Input Service name
        """
        return self.srv_input.name if self.srv_input else 'N/A'

    @property
    def type(self):
        """ Input service type
        """
        return self.srv_input.type if self.srv_input else waves.const.TYPE_TEXT

    @property
    def label(self):
        """ Input service label"""
        return self.srv_input.label if self.srv_input else 'N/A'

    @property
    def file_path(self):
        """Absolute file path to associated file (if any)

        :return: path to file
        :rtype: unicode
        """
        if self.type == waves.const.TYPE_FILE:
            return os.path.join(self.job.input_dir, str(self.value))
        else:
            return ""

    @property
    def validated_value(self):
        """ May modify value (cast) according to related ServiceInput type

        :return: determined from related ServiceInput type
        """
        if self.type == waves.const.TYPE_FILE:
            return self.file_path
        elif self.type == waves.const.TYPE_BOOLEAN:
            return bool(self.value)
        elif self.type == waves.const.TYPE_TEXT:
            return self.value
        elif self.type == waves.const.TYPE_INTEGER:
            return int(self.value)
        elif self.type == waves.const.TYPE_FLOAT:
            return float(self.value)
        elif self.type == waves.const.TYPE_LIST:
            if self.value == 'None':
                return False
            return self.value
        else:
            logger.warn('No Input type !')
            raise ValueError("No type specified for input")

    def clean(self):
        if self.srv_input.mandatory and not self.srv_input.default and not self.value:
            raise ValidationError('Input %(input) is mandatory', params={'input': self.srv_input.label})
        super(JobInput, self).clean()

    @property
    def command_line_element(self, forced_value=None):
        """For each job input, according to related ServiceInput, return command line part for this parameter

        :param forced_value: Any forced value if needed
        :return: depends on parameter type
        """
        value = self.validated_value if forced_value is None else forced_value
        """try:
            if self.srv_input and self.srv_input.to_output.exists():
                # related service input is a output 'name' parameter
                value = os.path.join('outputs', value)
        except ObjectDoesNotExist:
            pass
        """
        if self.param_type == waves.const.OPT_TYPE_VALUATED:
            return '--%s=%s' % (self.name, value)
        elif self.param_type == waves.const.OPT_TYPE_SIMPLE:
            if value:
                return '-%s %s' % (self.name, value)
            else:
                return ''
        elif self.param_type == waves.const.OPT_TYPE_OPTION:
            if value:
                return '-%s' % self.name
            return ''
        elif self.param_type == waves.const.OPT_TYPE_NAMED_OPTION:
            if value:
                return '--%s' % self.name
            return ''
        elif self.param_type == waves.const.OPT_TYPE_POSIX:
            if value:
                return '%s' % value
            else:
                return ''
        elif self.param_type == waves.const.OPT_TYPE_NONE:
            return ''
        # By default it's OPT_TYPE_SIMPLE way
        return '-%s %s' % (self.name, self.value)

    @property
    def get_label_for_choice(self):
        return self.srv_input.get_value_for_choice(self.value)

    @property
    def display_online(self):
        return allow_display_online(self.file_path)


class JobOutput(OrderAble, SlugAble, UrlMixin):
    """ JobOutput is association fro a Job, a ServiceOutput, and the effective value set for this Job
    """
    class Meta:
        db_table = 'waves_job_output'
        unique_together = ('srv_output', 'job', 'value')
    #: Related :class:`waves.models.jobs.Job`
    job = models.ForeignKey(Job, related_name='job_outputs', on_delete=models.CASCADE)
    #: Related :class:`waves.models.services.ServiceOutput`
    srv_output = models.ForeignKey('ServiceOutput', null=True, on_delete=models.CASCADE)
    #: Job Output value
    value = models.CharField('Output value', max_length=200, null=True, blank=True, default="")
    #: Set whether this output may be empty (no output from Service)
    may_be_empty = models.BooleanField('MayBe empty', default=True)

    @property
    def name(self):
        # hard coded value for non service related output (stderr / stdout)
        if not self.srv_output:
            if self.value == self.job.stdout:
                return "Standard output"
            elif self.value == self.job.stderr:
                return "Standard error"
            else:
                return 'N/A'
        return self.srv_output.name

    @property
    def type(self):
        return self.srv_output.ext if self.srv_output else 'txt'

    def __str__(self):
        return '%s - %s' % (self.name, self.value)

    @property
    def file_path(self):
        return os.path.join(self.job.output_dir, self.value)

    @property
    def file_content(self):
        if os.path.isfile(self.file_path):
            with open(self.file_path, 'r') as f:
                return f.read()
        return None

    @property
    def link(self):
        return self.get_url()

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        return reverse('waves:job_output', kwargs={'slug': self.slug})

    @property
    def download_url(self):
        return "%s?export=1" % self.get_absolute_url()

    @property
    def display_online(self):
        return allow_display_online(self.file_path)


class JobHistory(models.Model):
    """ Represents a job status history event
    """
    class Meta:
        db_table = 'waves_job_history'
        ordering = ['-timestamp', '-status']
        unique_together = ('job', 'timestamp', 'status', 'is_admin')
    #: Related :class:`waves.models.jobs.Job`
    job = models.ForeignKey(Job, related_name='job_history', on_delete=models.CASCADE)
    #: Time when this event occurred
    timestamp = models.DateTimeField('Date time', auto_now_add=True, help_text='History timestamp')
    #: Job Status for this event
    status = models.IntegerField('Job Status', blank=False, null=False, choices=waves.const.STATUS_LIST,
                                 help_text='History job status')
    #: Job event message
    message = models.TextField('History log', blank=True, null=True, help_text='History log')
    #: Event is only intended for Admin
    is_admin = models.BooleanField('Admin Message', default=False)

    def __str__(self):
        return '%s:%s:%s' % (self.message, self.get_status_display(), self.job)


class JobAdminHistoryManager(models.Manager):
    def get_queryset(self):
        """
        Specific query set to filter only :class:`waves.models.jobs.JobAdminHistory` objects
        :return: QuerySet
        """
        return super(JobAdminHistoryManager, self).get_queryset().filter(is_admin=True)

    def create(self, **kwargs):
        """ Force 'is_admin' flag for JobAdminHistory models objects
        :return: a JobAdminHistory object
        """
        kwargs.update({'is_admin': True})
        return super(JobAdminHistoryManager, self).create(**kwargs)


class JobAdminHistory(JobHistory):
    """A Job Event intended only for Admin use
    """
    class Meta:
        proxy = True

    objects = JobAdminHistoryManager()


eav.register(Job, JobEavConfig)
eav.register(JobInput, JobInputEavConfig)
eav.register(JobOutput, JobOutputEavConfig)
