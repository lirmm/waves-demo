""" WVES job related models class objects """
from __future__ import unicode_literals

import json
import os
from os.path import join

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.html import format_html
from waves.exceptions import WavesException
from waves.exceptions.jobs import JobInconsistentStateError, JobRunException
from waves.models import TimeStamped, Slugged, Ordered, UrlMixin
from waves.models.adaptors import DTOMixin, AdaptorInitParam
from waves.models.inputs import BaseParam
from waves.models.managers.jobs import *
from waves.models.submissions import Submission
from waves.utils.jobs import default_run_details
from waves.utils.storage import allow_display_online
import waves_adaptors.exceptions.adaptors

__license__ = "MIT"
__revision__ = " $Id: actor.py 1586 2009-01-30 15:56:25Z cokelaer $ "
__docformat__ = 'reStructuredText'
__all__ = ['Job', 'JobInput', 'JobOutput', 'JobHistory', 'JobAdminHistory', 'JobRunParams']


class JobRunParams(AdaptorInitParam):
    """ Saved configuration for job runs """
    class Meta:
        proxy = True


class Job(TimeStamped, Slugged, UrlMixin, DTOMixin):
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

    STR_JOB_UNDEFINED = 'Unknown'
    STR_JOB_CREATED = 'Created'
    STR_JOB_PREPARED = 'Prepared for run'
    STR_JOB_QUEUED = 'Queued'
    STR_JOB_RUNNING = 'Running'
    STR_JOB_COMPLETED = 'Completed'
    STR_JOB_TERMINATED = 'Finished'
    STR_JOB_CANCELLED = 'Cancelled'
    STR_JOB_SUSPENDED = 'Suspended'
    STR_JOB_ERROR = 'In Error'

    JOB_UNDEFINED = -1
    JOB_CREATED = 0
    JOB_PREPARED = 1
    JOB_QUEUED = 2
    JOB_RUNNING = 3
    JOB_SUSPENDED = 4
    JOB_COMPLETED = 5
    JOB_TERMINATED = 6
    JOB_CANCELLED = 7
    JOB_ERROR = 9

    STATUS_LIST = [
        (JOB_UNDEFINED, STR_JOB_UNDEFINED),
        (JOB_CREATED, STR_JOB_CREATED),
        (JOB_PREPARED, STR_JOB_PREPARED),
        (JOB_QUEUED, STR_JOB_QUEUED),
        (JOB_RUNNING, STR_JOB_RUNNING),
        (JOB_SUSPENDED, STR_JOB_SUSPENDED),
        (JOB_COMPLETED, STR_JOB_COMPLETED),
        (JOB_TERMINATED, STR_JOB_TERMINATED),
        (JOB_CANCELLED, STR_JOB_CANCELLED),
        (JOB_ERROR, STR_JOB_ERROR),
    ]
    NEXT_STATUS = {
        JOB_CREATED: JOB_PREPARED,
        JOB_PREPARED: JOB_QUEUED,
        JOB_QUEUED: JOB_RUNNING,
        JOB_RUNNING: JOB_COMPLETED,
        JOB_COMPLETED: JOB_TERMINATED
    }
    PENDING_STATUS = (JOB_CREATED,
                      JOB_PREPARED,
                      JOB_QUEUED,
                      JOB_RUNNING)

    class Meta(TimeStamped.Meta):
        db_table = 'waves_job'
        verbose_name = 'Job'
        ordering = ['-updated', '-created']

    objects = JobManager()
    #: Job Title, automatic or set by user upon submission
    title = models.CharField('Job title', max_length=255, null=True, blank=True)
    #: Job related Service - see :ref:`service-label`.
    submission = models.ForeignKey(Submission, related_name='service_jobs', null=False,
                                   on_delete=models.CASCADE)
    #: Job last known status - see :ref:`waves-jobconst-label`.
    status = models.IntegerField('Job status', choices=STATUS_LIST,
                                 default=JOB_CREATED,
                                 help_text='Job current run status')
    #: Job last status for which we sent a notification email
    status_mail = models.IntegerField(editable=False, default=9999)
    #: Job associated client, may be null for anonymous submission
    client = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE,
                               related_name='clients_job', help_text='Associated registered user')
    #: Email to notify job status to
    email_to = models.EmailField('Email results', null=True, blank=True, help_text='Notify results to this email')
    #: Job ExitCode (mainly for admin purpose)
    exit_code = models.IntegerField('Job system exit code', default=0, help_text="Job exit code on relative adaptor")
    #: Tell whether job results files are available for download from client
    results_available = models.BooleanField('Results are available', default=False, editable=False)
    #: Job last status retry count (max before Error set in conf)
    nb_retry = models.IntegerField('Nb Retry', editable=False, default=0)
    #: Jobs are remotely executed, store the adaptor job identifier
    remote_job_id = models.CharField('Remote job ID (on adaptor)', max_length=255, editable=False, null=True)
    #: Jobs sometime can gain access to a remote history, store the adaptor history identifier
    remote_history_id = models.CharField('Remote history ID (on adaptor)', max_length=255, editable=False, null=True)

    @property
    def service(self):
        """ Retrieve service """
        return self.submission.service

    def natural_key(self):
        """ Job natural keys """
        return self.slug, self.service.natural_key()

    def colored_status(self):
        """
        Format a row depending on current Job Status
        :return: Html unicode string
        """
        return format_html('<span class="{}">{}</span>',
                           self.label_class,
                           self.get_status_display())

    def save(self, *args, **kwargs):
        """ Overriden save, set _status to current job status """
        super(Job, self).save(*args, **kwargs)
        self._status = self.status

    def make_job_dirs(self):
        """
        Create job working dirs
        :return: None
        """
        if not os.path.isdir(self.working_dir):
            os.makedirs(self.working_dir, mode=0775)

    def delete_job_dirs(self):
        """Upon job deletion in database, cleanup associated working dirs
        :return: None
        """
        import shutil
        shutil.rmtree(self.working_dir, ignore_errors=True)

    @classmethod
    def from_db(cls, db, field_names, values):
        """ Overridden, set up _status to last DB value """
        instance = super(Job, cls).from_db(db, field_names, values)
        instance._status = instance.status
        return instance

    @property
    def changed_status(self):
        """ Tells whether loaded object status is different from the one issued from last retrieve in db
        :return: True if changed, False either
        :rtype: bool
        """
        return self._status != self.status

    @property
    def input_files(self):
        """ Get only 'files' inputs for job
        :return: list of JobInput models instance
        :rtype: QuerySet
        """
        return self.job_inputs.filter(type=BaseParam.TYPE_FILE)

    @property
    def output_files_exists(self):
        """ Check if expected outputs are present on disk, return only those ones
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
        """ Return list of all outputs files, whether they exist or not on disk
        .. note::
            Use :func:`output_files_exists` for only existing outputs instead
        :return: a list of JobOuput objects
        :rtype: list
        """
        all_files = self.job_outputs.all()
        return all_files

    @property
    def input_params(self):
        """ Return all non-file (i.e tool params) job inputs, i.e job execution parameters
        :return: list of `JobInput` models instance
        :rtype: QuerySet
        """
        return self.job_inputs.exclude(type=BaseParam.TYPE_FILE)

    @property
    def working_dir(self):
        """Base job working dir

        :return: working dir
        :rtype: unicode
        """
        return os.path.join(settings.WAVES_JOB_DIR, str(self.slug))

    @property
    def adaptor(self):
        """ Return current related service adaptor effective class
        :return: a child class of `JobRunnerAdaptor`
        :rtype: `waves_adaptors.runner.JobRunnerAdaptor`
        """
        return self.submission.adaptor

    def __str__(self):
        return '[%s][%s]' % (self.slug, self.service.api_name)

    @property
    def command(self):
        """ Return current related service command effective class
        :return: a BaseCommand object (or one of its child)
        :rtype: `BaseCommand`
        """
        return self.service.command

    @property
    def command_line(self):
        """ Generate full command line for Job
        :return: string representation of command line
        :rtype: unicode
        """
        return "%s %s" % (self.adaptor.command, self.command.create_command_line(job_inputs=self.job_inputs.all()))

    @property
    def label_class(self):
        """Return css class label associated with current Job Status
        :return: a css class (based on bootstrap)
        :rtype: unicode
        """
        if self.status in (self.JOB_UNDEFINED, self.JOB_SUSPENDED):
            return 'warning'
        elif self.status == self.JOB_ERROR:
            return 'danger'
        elif self.status == self.JOB_CANCELLED:
            return 'info'
        else:
            return 'success'

    def check_send_mail(self):
        """According to job status, check needs for sending notification emails
        :return: the nmmber of mail sent (should be one)
        :rtype: int
        """
        from waves.managers.mails import JobMailer
        mailer = JobMailer(job=self)
        if self.status != self.status_mail and self.status == self.JOB_ERROR:
            mailer.send_job_admin_error()
        if settings.WAVES_NOTIFY_RESULTS and self.service.email_on:
            if self.email_to is not None and self.status != self.status_mail:
                # should send a email
                try:
                    nb_sent = 0
                    if self.status == self.JOB_CREATED:
                        nb_sent = mailer.send_job_submission_mail()
                    elif self.status == self.JOB_TERMINATED:
                        nb_sent = mailer.send_job_completed_mail()
                    elif self.status == self.JOB_ERROR:
                        nb_sent = mailer.send_job_error_email()
                    elif self.status == self.JOB_CANCELLED:
                        nb_sent = mailer.send_job_cancel_email()
                    # Avoid resending emails when last status mail already sent
                    self.status_mail = self.status
                    if nb_sent > 0:
                        self.job_history.add(JobAdminHistory.objects.create(message='Sent notification email',
                                                                            status=self.status, job=self))
                    else:
                        self.job_history.add(JobAdminHistory.objects.create(message='Mail not sent',
                                                                            status=self.status, job=self))
                    self.save()
                    return nb_sent
                except Exception as e:
                    logger.error('Unable to send mail : %s', e)
                    pass

    def get_absolute_url(self):
        """Reverse url for this Job according to Django urls configuration
        :return: the absolute uri of this job (without host)
        """
        from django.core.urlresolvers import reverse
        return reverse('waves:job_details', kwargs={'slug': self.slug})

    @property
    def details_available(self):
        """Check whether run details are available for this JOB

        .. note::
            Not really yet implemented

        :return: True is exists, False either
        :rtype: bool
        """
        return os.path.isfile(os.path.join(self.working_dir, 'run_details.p'))

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
        for service_input in service_submission.submission_inputs.filter(required=False):
            # Create fake "submitted_inputs" with non editable ones with default value if not already set
            logger.debug('Created non editable job input: %s (%s, %s)', service_input.label,
                         service_input.name, service_input.default)
            self.job_inputs.add(JobInput.objects.create(job=self, name=service_input.name,
                                                        type=service_input.type,
                                                        param_type=service_input.param_type,
                                                        label=service_input.label,
                                                        order=service_input.order,
                                                        value=service_input.default))

    def create_default_outputs(self):
        """ Create standard default outputs for job (stdout and stderr)
        :return: None
        """
        output_dict = dict(job=self, value=self.stdout, optional=False, _name='Standard output', type="txt")
        out = JobOutput.objects.create(**output_dict)
        self.job_outputs.add(out)
        open(join(self.working_dir, self.stdout), 'a').close()
        output_dict['value'] = self.stderr
        output_dict['_name'] = "Standard error"
        out1 = JobOutput.objects.create(**output_dict)
        self.job_outputs.add(out1)
        open(join(self.working_dir, self.stderr), 'a').close()
        logger.debug('Created default outputs: [%s, %s]', out, out1)

    @property
    def public_history(self):
        """Filter Job history elements for public (non `JobAdminHistory` elements)

        :rtype: QuerySet
        """
        return self.job_history.filter(is_admin=False)

    def retry(self, message):
        """ Add a new try for job execution, save retry reason in JobAdminHistory, save job """
        if self.nb_retry <= settings.WAVES_JOBS_MAX_RETRY:
            self.nb_retry += 1
            JobAdminHistory.objects.create(job=self, message='[Retry]%s' % message, status=self.status)
            self.save()
        else:
            self.error(message)

    def error(self, message):
        """ Set job Status to ERROR, save error reason in JobAdminHistory, save job"""
        self.status = self.JOB_ERROR
        JobAdminHistory.objects.create(job=self, message='[Error]%s' % message, status=self.status)
        self.save()

    def fatal_error(self, exception):
        logger.exception(exception)
        self.error(exception.message)

    def save_status_history(self, state=None, message=None):
        """ Save new state in DB, add history message id needed """
        h_message = message or self.message or 'Job %s' % self.get_status_display().lower()
        JobHistory.objects.create(job=self, message=h_message, status=state or self.status)
        logger.debug('Job [%s] status set to [%s]', self.slug, self.get_status_display())

    def _run_action(self, action):
        """ Check if current job status is coherent with requested action """
        if action == 'prepare_job':
            status_allowed = self.STATUS_LIST[1:2]
        elif action == 'run_job':
            status_allowed = self.STATUS_LIST[2:3]
        elif action == 'cancel_job':
            # Report fails to a AdaptorException raise during cancel process
            status_allowed = self.STATUS_LIST
            if getattr(self.adaptor, 'state_allow_cancel', None):
                status_allowed = self.adaptor.state_allow_cancel
        elif action == 'job_results':
            status_allowed = self.STATUS_LIST[6:7] + self.STATUS_LIST[9:]
        elif action == 'job_run_details':
            status_allowed = self.STATUS_LIST[6:10]
        else:
            # By default let all status allowed
            status_allowed = self.STATUS_LIST
        if self.status not in [int(i[0]) for i in status_allowed]:
            raise JobInconsistentStateError(self.get_status_display(), status_allowed)
        try:
            returned = getattr(self.adaptor, action)(self)
            self.nb_retry = 0
            self.save()
            return returned
        except waves_adaptors.exceptions.adaptors.AdaptorException as exc:
            self.retry(exc.message)
            raise JobRunException('[%s][%s] %s' % (action, exc.__class__.__name__, str(exc)), job=self)
        except WavesException as exc:
            self.error(exc.message)
            raise exc
        except Exception as exc:
            self.fatal_error(exc)
            raise JobRunException('[%s][%s] %s' % (action, exc.__class__.__name__, str(exc)), job=self)

    @property
    def next_status(self):
        """ Automatically retrieve next expected status """
        try:
            logger.debug("next status %s", self.NEXT_STATUS[self.status])
            return self.NEXT_STATUS[self.status]
        except KeyError:
            return self.status

    def run_prepare(self):
        """ Ask job adaptor to prepare run (manage input files essentially) """
        self._run_action('prepare_job')
        self.save_status_history()

    def run_launch(self):
        """ Ask job adaptor to actually launch job """
        self._run_action('run_job')
        self.save_status_history()

    def run_status(self):
        """ Ask job adaptor current job status """
        self.status = self._run_action('job_status')
        logger.debug('job current state :%s', self.status)
        self.save()
        if self.status == self.JOB_COMPLETED:
            self.run_results()
        if self.status == self.JOB_UNDEFINED and self.nb_retry > settings.WAVES_JOBS_MAX_RETRY:
            self.run_cancel()
        self.save_status_history()
        return self.status

    def run_cancel(self):
        """ Ask job adaptor to cancel job if possible """
        self._run_action('cancel_job')
        self.message = 'Job cancelled'
        self.save_status_history(self.JOB_CANCELLED)

    def run_results(self):
        """ Ask job adaptor to get results files (dowload files if needed) """
        self._run_action('job_results')
        self.run_details()
        if self.exit_code != 0 or len(self.stderr_txt) > 0:
            self.save_status_history(state=self.JOB_ERROR, message=self.stderr_txt)
        else:
            self.save_status_history(state=self.JOB_TERMINATED)
        self.save()

    def run_details(self):
        """ Ask job adaptor to get JobRunDetails information (started, finished, exit_code ...)"""
        from waves_adaptors.core.base import JobRunDetails
        file_run_details = join(self.working_dir, 'job_run_details.json')
        if os.path.isfile(file_run_details):
            # Details have already been downloaded
            with open(file_run_details) as fp:
                details = JobRunDetails(*json.load(fp))
            return details
        else:
            try:
                remote_details = self._run_action('job_run_details')
            except waves_adaptors.exceptions.adaptors.AdaptorException:
                remote_details = default_run_details(self)
                with open(file_run_details, 'w') as fp:
                    json.dump(obj=remote_details, fp=fp, ensure_ascii=False)
            return remote_details

    @property
    def stdout_txt(self):
        """Retrieve stdout content for this job"""
        with open(join(self.working_dir, self.stdout), 'r') as fp:
            return fp.read()

    @property
    def stderr_txt(self):
        with open(join(self.working_dir, self.stderr), 'r') as fp:
            return fp.read()

    @property
    def allow_rerun(self):
        """ set whether current job state allow rerun """
        return self.status not in (self.JOB_CREATED, self.JOB_UNDEFINED)

    def re_run(self):
        """ Reset attributes and mark job as CREATED to be re-run"""
        # self.job_history.all().delete()
        self.message = "Job marked for re-run"
        self.nb_retry = 0
        self.status = self.JOB_CREATED
        for job_out in self.job_outputs.all():
            open(job_out.file_path, 'w').close()
        self.save()


class JobInput(Ordered, Slugged):
    """
    Job Inputs is association between a Job, a SubmissionParam, setting a value specific for this job
    """

    class Meta:
        db_table = 'waves_job_input'
        unique_together = ('name', 'job')

    objects = JobInputManager()
    #: Reference to related :class:`waves.models.jobs.Job`
    job = models.ForeignKey(Job, related_name='job_inputs', on_delete=models.CASCADE)
    #: Reference to related :class:`waves.models.services.SubmissionParam`
    # srv_input = models.ForeignKey('SubmissionParam', null=True, on_delete=models.CASCADE)
    #: Value set to this service input for this job
    value = models.CharField('Input content', max_length=255, null=True, blank=True,
                             help_text='Input value (filename, boolean value, int value etc.)')
    #: Each input may have its own identifier on remote adaptor
    remote_input_id = models.CharField('Remote input ID (on adaptor)', max_length=255, editable=False, null=True)
    type = models.CharField('Param type', choices=BaseParam.IN_TYPE, max_length=50, editable=False, null=True)
    name = models.CharField('Param name', max_length=200, editable=False, null=True)
    param_type = models.IntegerField('Parameter Type', choices=BaseParam.OPT_TYPE, editable=False,
                                     default=BaseParam.OPT_TYPE_POSIX)
    label = models.CharField('Label', max_length=100, editable=False, null=True)

    def natural_key(self):
        return self.job.natural_key(), self.name

    def save(self, *args, **kwargs):
        super(JobInput, self).save(*args, **kwargs)

    def __str__(self):
        return u'|'.join([self.name, str(self.value)])

    @property
    def file_path(self):
        """Absolute file path to associated file (if any)

        :return: path to file
        :rtype: unicode
        """
        if self.type == BaseParam.TYPE_FILE:
            return os.path.join(self.job.working_dir, str(self.value))
        else:
            return ""

    @property
    def validated_value(self):
        """ May modify value (cast) according to related SubmissionParam type

        :return: determined from related SubmissionParam type
        """
        if self.type == BaseParam.TYPE_FILE:
            return self.value
        elif self.type == BaseParam.TYPE_BOOLEAN:
            return bool(self.value)
        elif self.type == BaseParam.TYPE_TEXT:
            return self.value
        elif self.type == BaseParam.TYPE_INT:
            return int(self.value)
        elif self.type == BaseParam.TYPE_DECIMAL:
            return float(self.value)
        elif self.type == BaseParam.TYPE_LIST:
            if self.value == 'None':
                return False
            return self.value
        else:
            logger.warn('No Input type !')
            raise ValueError("No type specified for input")

    @property
    def srv_input(self):
        return self.job.submission.submission_inputs.filter(name=self.name).first()

    def clean(self):
        if self.srv_input.mandatory and not self.srv_input.default and not self.value:
            raise ValidationError('Input %(input) is mandatory', params={'input': self.srv_input.label})
        super(JobInput, self).clean()

    @property
    def command_line_element(self, forced_value=None):
        """For each job input, according to related SubmissionParam, return command line part for this parameter

        :param forced_value: Any forced value if needed
        :return: depends on parameter type
        """
        value = self.validated_value if forced_value is None else forced_value
        if self.param_type == BaseParam.OPT_TYPE_VALUATED:
            return '--%s=%s' % (self.name, value)
        elif self.param_type == BaseParam.OPT_TYPE_SIMPLE:
            if value:
                return '-%s %s' % (self.name, value)
            else:
                return ''
        elif self.param_type == BaseParam.OPT_TYPE_OPTION:
            if value:
                return '-%s' % self.name
            return ''
        elif self.param_type == BaseParam.OPT_TYPE_NAMED_OPTION:
            if value:
                return '--%s' % self.name
            return ''
        elif self.param_type == BaseParam.OPT_TYPE_POSIX:
            if value:
                return '%s' % value
            else:
                return ''
        elif self.param_type == BaseParam.OPT_TYPE_NONE:
            return ''
        # By default it's OPT_TYPE_SIMPLE way
        return '-%s %s' % (self.name, self.value)

    @property
    def get_label_for_choice(self):
        """ Try to get label for value issued from a service list input"""
        from waves.models.inputs import BaseParam
        try:
            srv_input = BaseParam.objects.get(submission=self.job.submission,
                                              name=self.name)
            return srv_input.get_choises(self.value)
        except ObjectDoesNotExist:
            pass
        return self.value

    @property
    def display_online(self):
        return allow_display_online(self.file_path)


class JobOutput(Ordered, Slugged, UrlMixin):
    """ JobOutput is association fro a Job, a SubmissionOutput, and the effective value set for this Job
    """

    class Meta:
        db_table = 'waves_job_output'
        unique_together = ('_name', 'job')

    objects = JobOutputManager()
    #: Related :class:`waves.models.jobs.Job`
    job = models.ForeignKey(Job, related_name='job_outputs', on_delete=models.CASCADE)
    #: Related :class:`waves.models.services.SubmissionOutput`
    # srv_output = models.ForeignKey('SubmissionOutput', null=True, on_delete=models.CASCADE)
    #: Job Output value
    value = models.CharField('Output value', max_length=200, null=True, blank=True, default="")
    #: Set whether this output may be empty (no output from Service)
    optional = models.BooleanField('MayBe empty', default=True)
    #: Each output may have its own identifier on remote adaptor
    remote_output_id = models.CharField('Remote output ID (on adaptor)', max_length=255, editable=False, null=True)
    _name = models.CharField('Name', max_length=200, null=False, blank=False, help_text='Output displayed name')
    type = models.CharField('File extension', max_length=5, null=False, default=".txt")

    @property
    def name(self):
        # hard coded value for non service related output (stderr / stdout)
        if self.value == self.job.stdout:
            return "Standard output"
        elif self.value == self.job.stderr:
            return "Standard error"
        return self._name

    def natural_key(self):
        return self.job.natural_key(), self._name

    def __str__(self):
        return '%s - %s' % (self.name, self.value)

    @property
    def file_path(self):
        return os.path.join(self.job.working_dir, self.value)

    @property
    def file_content(self):
        if os.path.isfile(self.file_path):
            with open(self.file_path, 'r') as f:
                return f.read()
        return None

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

    objects = JobHistoryManager()
    #: Related :class:`waves.models.jobs.Job`
    job = models.ForeignKey(Job, related_name='job_history', on_delete=models.CASCADE, null=False)
    #: Time when this event occurred
    timestamp = models.DateTimeField('Date time', auto_now_add=True, help_text='History timestamp')
    #: Job Status for this event
    status = models.IntegerField('Job Status', choices=Job.STATUS_LIST,
                                 help_text='History job status')
    #: Job event message
    message = models.TextField('History log', blank=True, null=True, help_text='History log')
    #: Event is only intended for Admin
    is_admin = models.BooleanField('Admin Message', default=False)

    def __str__(self):
        return '%s:%s:%s' % (self.get_status_display(), self.job, self.message) + ('(admin)' if self.is_admin else '')


class JobAdminHistory(JobHistory):
    """A Job Event intended only for Admin use
    """

    class Meta:
        proxy = True

    objects = JobAdminHistoryManager()
