from __future__ import unicode_literals
import os
import logging
import eav
from collections import namedtuple
from django.conf import settings
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.utils.html import format_html
from django.core.exceptions import ValidationError

import waves.const as const
from waves.eav.config import JobEavConfig, JobInputEavConfig, JobOutputEavConfig
from waves.managers.jobs import JobManager
from waves.models import TimeStampable, SlugAble, OrderAble
import waves.settings

logger = logging.getLogger(__name__)

RunJobInfo = namedtuple("RunJobInfo",
                        """jobId hasExited hasSignal terminatedSignal hasCoreDump
                           wasAborted exitStatus resourceUsage""")


class Job(TimeStampable, SlugAble):
    """
    Store current jobs created by the platform
    """
    # non persistent field, used for history savings see signals
    message = None
    _status = None
    status_time = None
    _run_details = None

    class Meta(TimeStampable.Meta):
        db_table = 'waves_job'
        verbose_name = 'Job'
        unique_together = (('service', 'slug'),)

    objects = JobManager()

    title = models.CharField('Job title', max_length=255, null=True, blank=True)

    service = models.ForeignKey('Service', related_name='service_jobs', null=False, on_delete=models.CASCADE)
    status = models.IntegerField('Job status', choices=const.STATUS_LIST, default=const.JOB_CREATED,
                                 help_text='Job current run status')
    status_mail = models.IntegerField(editable=False, default=9999)
    client = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE,
                               related_name='clients_job', help_text='Associated registered user')
    email_to = models.EmailField('Email results', null=True, blank=True,
                                 help_text='Notify results to this email')

    exit_code = models.IntegerField('Job system exit code', null=False, default=0,
                                    help_text="Job exit code on relative runner")
    results_available = models.BooleanField('Results are available', default=False, editable=False)

    remote_job_id = models.CharField('Remote Job ID (on runner)', max_length=255, editable=False, null=True)
    nb_retry = models.IntegerField('Nb Retry', editable=False, default=0)

    def __init__(self, *args, **kwargs):
        super(Job, self).__init__(*args, **kwargs)
        self._status = self.status

    def colored_status(self):
        return format_html('<span class="{}">{}</span>',
                           self.label_class,
                           self.get_status_display())

    def save(self, *args, **kwargs):
        """
        Override save method to initialize some "non db related" attributes
        Args:
        Returns:
            None
        """
        super(Job, self).save(*args, **kwargs)
        self._status = self.status

    def make_job_dirs(self):
        if not os.path.isdir(self.input_dir):
            os.makedirs(self.input_dir, mode=0775)
        if not os.path.isdir(self.output_dir):
            os.makedirs(self.output_dir, mode=0775)
        os.chmod(self.working_dir, 0775)
        os.chmod(self.input_dir, 0775)
        os.chmod(self.output_dir, 0775)

    def delete_job_dirs(self):
        import shutil
        shutil.rmtree(self.working_dir, ignore_errors=True)

    @classmethod
    def from_db(cls, db, field_names, values):
        instance = super(Job, cls).from_db(db, field_names, values)
        instance._status = instance.status
        return instance

    def has_changed_status(self):
        return self._status != self.status

    @property
    def input_files(self):
        return self.job_inputs.filter(srv_input__type=const.TYPE_FILE)

    @property
    def output_files_exists(self):
        all_files = self.job_outputs.all()
        existing = []
        for _file in all_files:
            if os.path.isfile(_file.file_path) and os.path.getsize(_file.file_path) > 0:
                existing.append(_file)
        return existing

    @property
    def input_params(self):
        return self.job_inputs.exclude(srv_input__type=const.TYPE_FILE)

    @property
    def input_dir(self):
        return os.path.join(self.working_dir, 'inputs/')

    @property
    def output_dir(self):
        return os.path.join(self.working_dir, 'outputs/')

    @property
    def working_dir(self):
        return os.path.join(waves.settings.WAVES_JOB_DIR, str(self.slug))

    @property
    def runner(self):
        return self.service.runner

    def __str__(self):
        return '%s [%s][%s]' % (self.title, self.service.api_name, self.slug)

    @property
    def command(self):
        return self.service.command

    @property
    def command_line(self):
        return self.command.create_command_line(job_inputs=self.job_inputs.all())

    @property
    def label_class(self):
        if self.status in (const.JOB_UNDEFINED, const.JOB_SUSPENDED):
            return 'warning'
        elif self.status == const.JOB_ERROR:
            return 'danger'
        elif self.status == const.JOB_CANCELLED:
            return 'info'
        else:
            return 'success'

    def check_send_mail(self):
        from waves.managers.mails import JobMailer
        if waves.settings.WAVES_NOTIFY_RESULTS and self.service.email_on:
            if self.email_to is not None and self.status != self.status_mail:
                # should send a email
                try:
                    nb_sent = 0
                    mailer = JobMailer(job=self)
                    if self.status == const.JOB_CREATED:
                        nb_sent = mailer.send_job_submission_mail()
                    elif self.status == const.JOB_TERMINATED:
                        nb_sent = mailer.send_job_completed_mail()
                    elif self.status == const.JOB_ERROR:
                        nb_sent = mailer.send_job_error_email()
                    elif self.status == const.JOB_CANCELLED:
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
                    if waves.settings.WAVES_DEBUG:
                        raise e

    def get_absolute_url(self):
        return reverse('waves:job_details', kwargs={'slug': self.slug})

    @property
    def link(self):
        return '%s%s' % (Site.objects.get_current().domain, self.get_absolute_url())

    @property
    def details_available(self):
        return os.path.isfile(os.path.join(self.working_dir, 'run_details.p'))

    def load_run_details(self):
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
        return 'job.stdout'

    @property
    def stderr(self):
        return 'job.stderr'

    def results_file_available(self):
        return all(os.path.isfile(e.file_path) for e in self.job_outputs.filter(may_be_empty=False))

    def create_non_editable_inputs(self):
        """
        Create non editable (== not submitted anywhere and used for run)
        Used in post_save signal
        Returns:
            None
        """
        for service_input in self.service.service_inputs.filter(editable=False) \
                .exclude(param_type=const.OPT_TYPE_NONE):
            # Create fake "submitted_inputs" with non editable ones with default value if not already set
            logger.debug('Created non editable job input: %s (%s, %s)', service_input.label,
                         service_input.name, service_input.default)
            self.job_inputs.add(JobInput.objects.create(job=self, srv_input=service_input,
                                                        order=service_input.order,
                                                        value=service_input.default))

    def create_default_outputs(self):
        """
        Create standard default outputs for job (stdout and stderr)
        Used in post_save signal
        Returns:
            None
        """
        output_dict = dict(job=self, value='job.stdout', may_be_empty=True, srv_output=None)
        out = JobOutput.objects.create(**output_dict)
        self.job_outputs.add(out)
        output_dict['value'] = 'job.stderr'
        out1 = JobOutput.objects.create(**output_dict)
        self.job_outputs.add(out1)
        logger.debug('Created default outputs: [%s, %s]', out, out1)


class JobInput(OrderAble, SlugAble):
    class Meta:
        db_table = 'waves_job_input'
        unique_together = ('srv_input', 'job', 'value')

    job = models.ForeignKey(Job,
                            related_name='job_inputs',
                            on_delete=models.CASCADE)
    srv_input = models.ForeignKey('BaseInput', null=True, on_delete=models.CASCADE)

    value = models.CharField('Input content',
                             max_length=255,
                             null=True,
                             blank=True,
                             help_text='Input value (filename, boolean value, int value etc.)',
                             )

    def __str__(self):
        return u'|'.join([self.name, str(self.value)])

    @property
    def param_type(self):
        return self.srv_input.param_type if self.srv_input else const.OPT_TYPE_POSIX

    @property
    def name(self):
        return self.srv_input.name if self.srv_input else 'N/A'

    @property
    def type(self):
        return self.srv_input.type if self.srv_input else const.TYPE_TEXT

    @property
    def label(self):
        return self.srv_input.label if self.srv_input else 'N/A'

    @property
    def file_path(self):
        if self.type == const.TYPE_FILE:
            return os.path.join(self.job.input_dir, str(self.value))
        else:
            return ""

    @property
    def validated_value(self):
        if self.type == const.TYPE_FILE:
            # return self.file_path
            # FIXME related path is hardcoded
            return 'inputs/' + self.value
        elif self.type == const.TYPE_BOOLEAN:
            return bool(self.value)
        elif self.type == const.TYPE_TEXT:
            return self.value
        elif self.type == const.TYPE_INTEGER:
            return int(self.value)
        elif self.type == const.TYPE_FLOAT:
            return float(self.value)
        elif self.type == const.TYPE_LIST:
            if self.value == 'None':
                return False
            return self.value
        else:
            logger.warn('No Input type !')
            raise ValueError("No type specified for input")

    def clean(self):
        print "in clean method ! ", self.name
        if self.srv_input.mandatory and not self.srv_input.default and not self.value:
            raise ValidationError('Input %(input) is mandatory', params={'input': self.srv_input.label})
        super(JobInput, self).clean()

    @property
    def command_line_element(self, forced_value=None):
        value = self.validated_value if forced_value is None else forced_value
        try:
            if self.srv_input and self.srv_input.to_output.exists():
                # related service input is a output 'name' parameter
                value = os.path.join('outputs', value)
        except ObjectDoesNotExist:
            pass
        if self.param_type == const.OPT_TYPE_VALUATED:
            return '--%s=%s' % (self.name, value)
        elif self.param_type == const.OPT_TYPE_SIMPLE:
            if value:
                return '-%s %s' % (self.name, value)
            else:
                return ''
        elif self.param_type == const.OPT_TYPE_OPTION:
            if value:
                return '-%s' % self.name
            return ''
        elif self.param_type == const.OPT_TYPE_NAMED_OPTION:
            if value:
                return '--%s' % self.name
            return ''
        elif self.param_type == const.OPT_TYPE_POSIX:
            if value:
                return '%s' % value
            else:
                return ''
        elif self.param_type == const.OPT_TYPE_NONE:
            return ''
        # By default it's OPT_TYPE_SIMPLE way
        return '-%s %s' % (self.name, self.value)

    @property
    def get_label_for_choice(self):
        return self.srv_input.get_value_for_choice(self.value)


def file_path(instance, filename):
    return instance.file_path


class JobOutput(OrderAble, SlugAble):
    class Meta:
        db_table = 'waves_job_output'
        unique_together = ('srv_output', 'job', 'value')

    job = models.ForeignKey(Job,
                            related_name='job_outputs',
                            on_delete=models.CASCADE)
    srv_output = models.ForeignKey('ServiceOutput',
                                   null=True,
                                   on_delete=models.CASCADE)
    value = models.CharField('Output value',
                             max_length=200,
                             null=True,
                             blank=True,
                             default="")
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
        return '%s%s' % (Site.objects.get_current().domain, self.get_absolute_url())

    def get_absolute_url(self):
        return reverse('waves:job_output', kwargs={'slug': self.slug})


class JobHistory(models.Model):
    class Meta:
        db_table = 'waves_job_history'
        ordering = ['-timestamp']
        unique_together = ('job', 'timestamp')

    job = models.ForeignKey(Job,
                            related_name='job_history',
                            on_delete=models.CASCADE)
    timestamp = models.DateTimeField('Date time', auto_now_add=True,
                                     help_text='History timestamp')
    status = models.IntegerField('Job Status',
                                 blank=False,
                                 null=False,
                                 choices=const.STATUS_LIST,
                                 help_text='History job status')
    message = models.TextField('History log',
                               blank=True,
                               null=True,
                               help_text='History log')
    is_admin = models.BooleanField('Admin Message', default=False)

    def __str__(self):
        return '%s:%s:%s' % (self.message, self.get_status_display(), self.job)


class JobAdminHistory(JobHistory):
    class Meta:
        proxy = True

    id_admin = True


eav.register(Job, JobEavConfig)
eav.register(JobInput, JobInputEavConfig)
eav.register(JobOutput, JobOutputEavConfig)
