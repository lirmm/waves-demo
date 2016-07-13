from __future__ import unicode_literals

import logging
from django.conf import settings
from django.template.loader import get_template

from mail_templated import send_mail

logger = logging.getLogger(__name__)

"""
send_mail(template_name, context, from_email, recipient_list,
              fail_silently=False, auth_user=None, auth_password=None,
              connection=None, **kwargs)
    """


class JobMailer(object):
    _template_subject = None
    _template_mail = None

    def __init__(self, job):
        super(JobMailer, self).__init__()
        self.job = job

    def get_context_data(self):
        return {'job': self.job, 'WAVES_APP_NAME': settings.WAVES_APP_NAME}

    @property
    def mail_activated(self):
        return settings.WAVES_NOTIFY_RESULTS and self.job.service.email_on

    def _send_job_mail(self, template):
        if self.mail_activated:
            context = self.get_context_data()
            return send_mail(template_name=template, context=context, from_email=settings.WAVES_SERVICES_EMAIL,
                             recipient_list=[self.job.email_to], subject='Job Submitted',
                             fail_silently=not settings.DEBUG)
        else:
            # No mail sent since not activated (keep value returned at same type than send_mail
            return 0

    def send_job_submission_mail(self):
        return self._send_job_mail(template="emails/job_submitted.html")

    def send_job_completed_mail(self):
        return self._send_job_mail(template="emails/job_completed.html")

    def send_job_error_email(self):
        return self._send_job_mail(template="emails/job_error.html")
