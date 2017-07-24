"""
WAVES Automated models signals handlers
"""
from __future__ import unicode_literals

from django.db.models.signals import post_save
from django.dispatch import receiver

from waves.wcore.utils import get_service_model

Service = get_service_model()


@receiver(post_save, sender=Service)
def service_post_save_handler(sender, instance, created, **kwargs):
    """ job presave handler """
    pass
