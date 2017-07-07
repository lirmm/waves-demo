""" Profiles related signals """
import uuid
from django.conf import settings
from django.contrib.auth import user_logged_in
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from ipware.ip import get_real_ip

from profiles.models import UserProfile
from profiles.storage import profile_directory


@receiver(user_logged_in)
def login_action_handler(sender, user, **kwargs):
    """ Register user ip address upon login """
    request = kwargs.get('request')
    ip = get_real_ip(request)
    if ip is not None:
        user_prof = user.profile
        user_prof.ip = ip
        user_prof.save(update_fields=['ip'])
    else:
        ip = request.META.get('REMOTE_ADDR', None)
        if ip is not None:
            user_prof = user.profile
            user_prof.ip = ip
            user_prof.save(update_fields=['ip'])


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def profile_post_save_handler(sender, instance, created, **kwargs):
    """ Post save handler for Auth user model (create default UserProfile if needed) """
    if created:
        # Create the profile object, only if it is newly created
        profile = UserProfile(user=instance)
        profile.save()
    if instance.is_active and instance.profile.registered_for_api and not instance.profile.api_key:
        # User is activated, has registered for waves_api services, and do not have any api_key
        instance.profile.api_key = uuid.uuid1()
    if instance.is_active and not instance.profile.registered_for_api:
        instance.profile.api_key = None
    instance.profile.save()


@receiver(post_delete, sender=UserProfile)
def profile_post_delete_handler(sender, instance, **kwargs):
    """ Post delete handler for UserProfile model objects """
    import shutil
    import os
    if os.path.exists(os.path.join(settings.MEDIA_ROOT, profile_directory(instance, ''))):
        shutil.rmtree(os.path.join(settings.MEDIA_ROOT, profile_directory(instance, '')))
