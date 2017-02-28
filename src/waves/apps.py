"""
WAVES app Django application descriptor

"""
from __future__ import unicode_literals

from django.apps import AppConfig


class WavesAppConfig(AppConfig):
    """
    WAVES main application AppConfig, add signals for webapp
    """
    name = "waves"
    verbose_name = 'WAVES'

    def ready(self):
        """
        Executed once when WAVES application startup !
        Just import waves signals
        :return: None
        """
        import waves.signals
