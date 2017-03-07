"""
WAVES app Django application descriptor

"""
from __future__ import unicode_literals

from os.path import dirname
from django.apps import AppConfig
import waves_constance


class WavesAppConfig(AppConfig):
    """
    WAVES main application AppConfig, add signals for webapp
    """
    name = "waves"
    verbose_name = 'WAVES'
    path = dirname(__file__)

    def __init__(self, app_name, app_module):
        self.path = dirname(__file__)
        super(WavesAppConfig, self).__init__(app_name, app_module)

    def ready(self):
        """
        Executed once when WAVES application startup !
        Just import waves signals
        :return: None
        """
        import waves.signals
