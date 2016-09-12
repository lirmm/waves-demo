from __future__ import unicode_literals
import os
import logging
import shutil
import uuid

from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.auth.models import Group
from django.conf import settings
from django.contrib.auth.signals import user_logged_in
from ipware.ip import get_real_ip

import waves.const
import waves.settings
from waves.models import Job, JobHistory, Service, ServiceInputSample, ServiceInput, ServiceSubmission
from waves.models.profiles import APIProfile, profile_directory
logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Job)
def pre_job_save_handler(sender, instance, **kwargs):
    if not instance.title:
        instance.title = '%s_%s' % (instance.service.api_name, instance.slug)


@receiver(post_save, sender=Job)
def job_save_handler(sender, instance, created, **kwargs):
    if created:
        JobHistory.objects.create(job=instance, status=instance.status, message="Job Created", timestamp=timezone.now())
        # create job working dirs locally
        instance.make_job_dirs()
        # initiate default outputs
        instance.create_default_outputs()
    if instance.has_changed_status():
        if not instance.status_time:
            instance.status_time = timezone.now()
        JobHistory.objects.create(job=instance, status=instance.status, message=instance.message)


@receiver(post_delete, sender=Job)
def job_delete_handler(sender, instance, **kwargs):
    instance.delete_job_dirs()


@receiver(post_delete, sender=Service)
def service_input_files_delete(sender, instance, **kwargs):
    if os.path.exists(os.path.join(waves.settings.WAVES_SAMPLE_DIR, instance.api_name)):
        shutil.rmtree(os.path.join(waves.settings.WAVES_SAMPLE_DIR, instance.api_name))


@receiver(post_delete, sender=ServiceInputSample)
def service_sample_file_delete(sender, instance, **kwargs):
    instance.file.delete()


@receiver(post_delete, sender=ServiceInput)
def service_input_delete(sender, instance, **kwargs):
    if instance.input_samples.count() > 0:
        for sample in instance.input_samples.all():
            sample.file.delete()


@receiver(post_save, sender=Service)
def service_create_signal(sender, instance, created, **kwargs):
    sample_dir = os.path.join(waves.settings.WAVES_SAMPLE_DIR, instance.api_name)
    if created and not os.path.isdir(sample_dir):
        os.makedirs(sample_dir)
        instance.submissions.add(ServiceSubmission.objects.create(service=instance,
                                                                  label='default'))


@receiver(user_logged_in)
def login_action(sender, user, **kwargs):
    """
    Make action upon user login
    - Register user ip address
    """
    request = kwargs.get('request')
    ip = get_real_ip(request)
    if ip is not None:
        logger.debug('Login action fired %s [%s]', user, ip)
        user_prof = user.profile
        user_prof.ip = ip
        user_prof.save(update_fields=['ip'])
    else:
        ip = request.META.get('REMOTE_ADDR', None)
        if ip is not None:
            logger.debug('Login action fired %s [%s]', user, ip)
            user_prof = user.profile
            user_prof.ip = ip
            user_prof.save(update_fields=['ip'])


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile_handler(sender, instance, created, **kwargs):
    if created:
        # Create the profile object, only if it is newly created
        profile = APIProfile(user=instance)
        profile.save()
    if instance.is_active and instance.profile.registered_for_api and not instance.profile.api_key:
        # User is activated, has registered for api services, and do not have any api_key
        instance.profile.api_key = uuid.uuid1()
        logger.debug("Update api_key for %s %s", instance, instance.profile.api_key)
    if instance.is_active and not instance.profile.registered_for_api:
        instance.profile.api_key = None
    instance.profile.save()


@receiver(post_delete, sender=APIProfile)
def delete_profile_file(sender, instance, **kwargs):
    import shutil
    import os
    if os.path.exists(os.path.join(settings.MEDIA_ROOT, profile_directory(instance, ''))):
        shutil.rmtree(os.path.join(settings.MEDIA_ROOT, profile_directory(instance, '')))
