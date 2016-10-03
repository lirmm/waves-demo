from __future__ import unicode_literals

from django.apps import AppConfig
from django.core.checks import Error, register
import logging
logger = logging.getLogger(__name__)

class WavesApp(AppConfig):
    name = "waves"
    verbose_name = 'Web Application for Versatile & Easy Bio-informatics Services'

    def ready(self):
        """
        Executed once when WAVES application startup !
        :return:
        """
        from waves.models import signals


@register()
def check_waves_config(app_configs=('waves'), **kwargs):
    # TODO implements some control on WAVES configuration
    errors = []
    check_failed = False
    if check_failed:
        errors.append(
            Error(
                'an error',
                hint='A hint.',
                id='waves.E001',
            )
        )
    return errors
