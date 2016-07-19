from __future__ import unicode_literals
import os
import logging

import eav
from django.conf import settings
from django.db import models
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.utils.html import format_html

import waves.const as const
from waves.eav.config import JobEavConfig, JobInputEavConfig, JobOutputEavConfig
from waves.managers import JobManager
from waves.models.base import TimeStampable, SlugAble, OrderAble
from waves.models.services import Service, ServiceInput

logger = logging.getLogger(__name__)


class Job(TimeStampable, SlugAble):
    """
    Store current jobs created by the platform
    """
    # persistent field, used for history savings see signals
    message = None
    _status = None
    status_time = None
    _run_details = None

    class Meta(TimeStampable.Meta):
        db_table = 'waves_job'
        verbose_name = 'Job'

    objects = JobManager()

    title = models.CharField('Job title', max_length=255, null=True, blank=True)

    service = models.ForeignKey(Service, related_name='service_jobs', null=False, on_delete=models.CASCADE)
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

    def __init__(self, *args, **kwargs):
        super(Job, self).__init__(*args, **kwargs)
        self._status = self.status

    def colored_status(self):
        return format_html('<span class="{}">{}</span>',
                           self.label_class,
                           self.get_status_display())

    def save(self, *args, **kwargs):
        """
        Override save method to initialize some not required attributes
        Args:
        Returns:
            None
        """
        super(Job, self).save(*args, **kwargs)
        self._status = self.status

    def make_job_dirs(self):
        if not os.path.isdir(self.input_dir):
            os.makedirs(self.input_dir, mode=0755)
        if not os.path.isdir(self.output_dir):
            os.makedirs(self.output_dir, mode=0755)

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
        return self.job_inputs.filter(type=const.TYPE_FILE)

    @property
    def input_params(self):
        return self.job_inputs.exclude(type=const.TYPE_FILE)

    @property
    def input_dir(self):
        return os.path.join(self.working_dir, 'inputs/')

    @property
    def output_dir(self):
        return os.path.join(self.working_dir, 'outputs/')

    @property
    def working_dir(self):
        return os.path.join(settings.WAVES_JOB_DIR, str(self.slug))

    @property
    def runner(self):
        return self.service.runner

    def __str__(self):
        return '%s [%s][%s][%s]' % (self.title, self.service.api_name, self.slug, self.email_to)

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
        elif self.status in (const.JOB_ERROR, const.JOB_TERMINATED):
            return 'danger'
        elif self.status == const.JOB_CANCELLED:
            return 'info'
        else:
            return 'success'

    def check_send_mail(self):
        from waves.managers.mails import JobMailer
        if self.email_to is not None and self.status != self.status_mail:
            mailer = JobMailer(job=self)
            self.status_mail = self.status
            if self.status == const.JOB_CREATED:
                return mailer.send_job_submission_mail()
            elif self.status == const.JOB_TERMINATED:
                return mailer.send_job_completed_mail()
            elif self.status == const.JOB_ERROR:
                return mailer.send_job_error_email()

    def get_absolute_url(self):
        return reverse('waves:job_details', kwargs={'slug': self.slug})

    @property
    def link(self):
        return 'http://%s%s' % (Site.objects.get_current().domain, self.get_absolute_url())


class JobInput(OrderAble, SlugAble):
    class Meta:
        db_table = 'waves_job_input'

    job = models.ForeignKey(Job,
                            related_name='job_inputs',
                            on_delete=models.CASCADE)
    related_service_input = models.ForeignKey(ServiceInput, null=True, on_delete=models.SET_NULL)
    param_type = models.IntegerField('Parameter Type',
                                     choices=const.OPT_TYPE,
                                     null=False,
                                     default=const.OPT_TYPE_POSIX,
                                     help_text='Input type (used in command line)')
    name = models.CharField(max_length=20,
                            blank=True,
                            null=False,
                            help_text='This is the parameter name for the runs')
    type = models.CharField(max_length=50,
                            blank=False,
                            null=True,
                            choices=const.IN_TYPE,
                            help_text='Type of parameter (bool, int, text, file etc.)')
    value = models.CharField('Input content',
                             max_length=255,
                             null=True,
                             blank=True,
                             help_text='Input value (filename, boolean value, int value etc.)')

    def __str__(self):
        return u'|'.join([self.name, str(self.value)])

    @property
    def file_path(self):
        if self.type == const.TYPE_FILE:
            return os.path.join(self.job.input_dir, str(self.value))
        else:
            return ""

    @property
    def validated_value(self):
        if self.type == const.TYPE_FILE:
            return self.file_path
        elif self.type == const.TYPE_BOOLEAN:
            return bool(self.value)
        elif self.type == const.TYPE_TEXT:
            return self.value
        elif self.type == const.TYPE_INTEGER:
            return int(self.value)
        elif self.type == const.TYPE_FLOAT:
            return float(self.value)
        elif self.type == const.TYPE_LIST:
            # test value for boolean TODO update to be more efficient
            if self.value == 'None':
                return False
            return bool(eval(self.value))
        else:
            logger.warn('No Input type !')
            raise ValueError("No type specified for input")

    @property
    def command_line_element(self):
        value = self.validated_value
        if self.param_type == const.OPT_TYPE_VALUATED:
            return '--%s=%s' % (self.name, value)
        elif self.param_type == const.OPT_TYPE_SIMPLE:
            if value:
                return '-%s %s' % (self.name, value)
            else:
                return ''
        elif self.param_type == const.OPT_TYPE_OPTION:
            if self.type != const.TYPE_BOOLEAN:
                raise ValueError("Param type option must be boolean")
            if value:
                return '-%s' % self.name
            return ''
        elif self.param_type == const.OPT_TYPE_NAMED_OPTION:
            if self.type != const.TYPE_BOOLEAN:
                raise ValueError("Param type option must be boolean")
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
        return self.related_service_input.get_value_for_choice(self.value)


def file_path(instance, filename):
    return instance.file_path


class JobOutput(OrderAble, SlugAble):
    class Meta:
        db_table = 'waves_job_output'

    job = models.ForeignKey(Job,
                            related_name='job_outputs',
                            on_delete=models.CASCADE)
    name = models.CharField('Name',
                            max_length=200,
                            null=False,
                            blank=False,
                            help_text='This is the parameter name for the runs')
    label = models.CharField('Label',
                             max_length=255,
                             null=True,
                             blank=True,
                             help_text='This is the displayed name for output (default is name)')
    value = models.TextField('Output value',
                             null=True,
                             blank=True,
                             default="")
    type = models.CharField('Output file ext',
                            max_length=255,
                            null=True,
                            default=".txt",
                            blank=True)
    # TODO add a field to specify if output is available for client

    def __str__(self):
        return '%s - %s' % (self.label, self.name)

    @property
    def file_path(self):
        return os.path.join(self.job.output_dir, str(self.value))


class JobHistory(models.Model):
    class Meta:
        db_table = 'waves_job_history'
        ordering = ['-timestamp']

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
    message = models.TextField('Status message',
                               blank=True,
                               null=True,
                               help_text='History message')

    def __str__(self):
        return '%s:%s:%s' % (self.message, self.get_status_display(), self.job)


eav.register(Job, JobEavConfig)
eav.register(JobInput, JobInputEavConfig)
eav.register(JobOutput, JobOutputEavConfig)
