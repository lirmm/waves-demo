""" Profiles App description """
from __future__ import unicode_literals

from django.apps import AppConfig


class ProfileConfig(AppConfig):
    """ Profile Config """
    name = "profiles"
    verbose_name = 'User Profiles'

    def ready(self):
        from . import signals # noqa
