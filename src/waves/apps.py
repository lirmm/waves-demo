"""
WAVES app Django application descriptor

"""
from __future__ import unicode_literals

from django.apps import AppConfig
from django.core.checks import Error, register
import constance.apps


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


class WavesConstanceConfig(constance.apps.ConstanceConfig):
    verbose_name = 'WAVES Setup'
    verbose_name_plural = 'WAVES Setup'
