"""
WAVES app Django application descriptor

"""
from __future__ import unicode_literals

from django.apps import AppConfig
from django.core.checks import Error, register


class WavesApp(AppConfig):
    """
    WAVES main application AppConfig, add signals for webapp
    """
    name = "waves"
    verbose_name = 'Web Application for Versatile & Easy Bio-informatics Services'

    def ready(self):
        """
        Executed once when WAVES application startup !
        Just import waves signals
        :return: None
        """
        from waves.models import signals


@register()
def check_waves_config(app_configs=('waves'), **kwargs):
    """
    WAVES configuration check up, added to classic ``manage.py check`` Django command

    .. TODO:
        Add more control on WAVES configuration

    :param app_configs:
    :param kwargs:
    :return:
    """
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
