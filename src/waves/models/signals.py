"""
Waves models classes signals
Defining processes for jobs workflow
"""
from __future__ import unicode_literals
import os
import logging
import shutil

from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone

from django.conf import settings
from waves.models import Job, JobHistory, service_sample_directory, Service

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Job)
def pre_job_save_handler(sender, instance, **kwargs):
    if not instance.title:
        instance.title = '%s_%s' % (instance.service.api_name, instance.slug)
    instance.check_send_mail()


@receiver(post_save, sender=Job)
def job_save_handler(sender, instance, created, **kwargs):
    if created:
        JobHistory.objects.create(job=instance, status=instance.status, message="Job Created", timestamp=timezone.now())
        instance.make_job_dirs()
    if instance.has_changed_status():
        logger.debug('Changed status saved to history %s ' % instance.status)
        if not instance.status_time:
            instance.status_time = timezone.now()
        JobHistory.objects.create(job=instance, status=instance.status, message=instance.message)


@receiver(post_delete, sender=Job)
def job_delete_handler(sender, instance, **kwargs):
    instance.delete_job_dirs()


@receiver(post_delete, sender=Service)
def service_input_files_delete(sender, instance, **kwargs):
    if os.path.exists(os.path.join(settings.WAVES_SAMPLE_DIR, instance.api_name)):
        shutil.rmtree(os.path.join(settings.WAVES_SAMPLE_DIR, instance.api_name))


@receiver(post_save, sender=Service)
def service_create_media(sender, instance, created, **kwargs):
    sample_dir = os.path.join(settings.WAVES_SAMPLE_DIR, instance.api_name)
    if created and not os.path.isdir(sample_dir):
        os.makedirs(sample_dir)
