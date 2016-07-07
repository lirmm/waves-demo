from __future__ import unicode_literals
import uuid
import logging
from os.path import join

from django.db.models.signals import post_save, post_delete
from django.contrib.auth.models import Group
from django.dispatch import receiver
from django.conf import settings

import waves.const
from waves.models.profiles import APIProfile, profile_directory
from waves.models.services import Service
logger = logging.getLogger(__name__)


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
        try:
            instance.groups.add(Group.objects.get(name=settings.WAVES_GROUP_API))
        except Group.DoesNotExist:
            pass

        for service in Service.objects.api_public():
            logger.debug("Add service authorization : %s" % service)
            instance.profile.authorized_services.add(service)
    if instance.is_active and not instance.profile.registered_for_api:
        instance.profile.api_key = None
        instance.profile.authorized_services.remove()
        for service in Service.objects.all():
            service.authorized_clients.remove(instance.profile)
    instance.profile.save()


@receiver(post_delete, sender=APIProfile)
def delete_profile_file(sender, instance, **kwargs):
    import shutil
    import os
    if os.path.exists(join(settings.MEDIA_ROOT, profile_directory(instance, ''))):
        shutil.rmtree(join(settings.MEDIA_ROOT, profile_directory(instance, '')))
