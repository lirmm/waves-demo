from __future__ import unicode_literals

import logging

from django.utils import timezone
from django.core import mail
from django.conf import settings
from django.test import override_settings
from waves.tests.base import WavesBaseTestCase
from waves.models import Job, JobInput, JobOutput, Service
import waves.const
import waves.settings

logger = logging.getLogger(__name__)


@override_settings(
    WAVES_NOTIFY_RESULTS=True,
)
class JobMailTest(WavesBaseTestCase):
    @classmethod
    def setUpClass(cls):
        super(JobMailTest, cls).setUpClass()
        logger.info('EMAIL_BACKEND: %s', settings.EMAIL_BACKEND)

    def test_mail_job(self):
        job = Job.objects.create(
            service=Service.objects.create(name='Sample Service', email_on=True),
            email_to='marc@fake.com')
        job.job_inputs.add(JobInput.objects.create(name="param1", value="Value1", job=job))
        job.job_inputs.add(JobInput.objects.create(name="param2", value="Value2", job=job))
        job.job_inputs.add(JobInput.objects.create(name="param3", value="Value3", job=job))
        job.job_outputs.add(JobOutput.objects.create(name="out1", value="out1", job=job))
        job.job_outputs.add(JobOutput.objects.create(name="out2", value="out2", job=job))
        job.status_time = timezone.datetime.now()
        job.check_send_mail()
        self.assertEqual(len(mail.outbox), 1)
        sent_mail = mail.outbox[-1]
        self.assertTrue(job.service.name in sent_mail.subject)
        self.assertEqual(job.email_to, sent_mail.to[0])
        self.assertEqual(waves.settings.WAVES_SERVICES_EMAIL, sent_mail.from_email)
        logger.debug('Mail subject: %s', sent_mail.subject)
        logger.debug('Mail from: %s', sent_mail.from_email)
        logger.debug('Mail content: \n%s', sent_mail.body)
        job.status = waves.const.JOB_COMPLETED
        # job.save()
        job.check_send_mail()
        # no more mails
        self.assertEqual(len(mail.outbox), 1)

        job.status = waves.const.JOB_TERMINATED
        # job.save()
        job.check_send_mail()
        self.assertEqual(len(mail.outbox), 2)
        sent_mail = mail.outbox[-1]
        logger.debug('Mail subject: %s', sent_mail.subject)
        logger.debug('Mail from: %s', sent_mail.from_email)
        logger.debug('Mail content: \n%s', sent_mail.body)
        job.status = waves.const.JOB_ERROR
        # job.save()
        job.check_send_mail()
        self.assertEqual(len(mail.outbox), 3)
        sent_mail = mail.outbox[-1]
        logger.debug('Mail subject: %s', sent_mail.subject)
        logger.debug('Mail from: %s', sent_mail.from_email)
        logger.debug('Mail content: \n%s', sent_mail.body)
        job.status = waves.const.JOB_CANCELLED
        # job.save()
        job.check_send_mail()
        self.assertEqual(len(mail.outbox), 4)
        sent_mail = mail.outbox[-1]
        logger.debug('Mail subject: %s', sent_mail.subject)
        logger.debug('Mail from: %s', sent_mail.from_email)
        logger.debug('Mail content: \n%s', sent_mail.body)
