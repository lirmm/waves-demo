from __future__ import unicode_literals

from django.apps import AppConfig
from django.core.checks import Warning, register
from os.path import basename


class WavesDemoConfig(AppConfig):
    name = 'demo'


@register()
def check_waves_config(app_configs=('demo'), **kwargs):
    """
    .. TODO:
        Add more control on WAVES configuration

    :param app_configs:
    :param kwargs:
    :return:
    """
    errors = []
    # check values for SECRET_KEY
    from django.conf import settings
    if hasattr(settings, "WAVES_ENV_FILE") and basename(settings.WAVES_ENV_FILE) == "local.sample.env":
        errors.append(
            Warning(
                'You are using sample env configuration file',
                hint='Rename local.sample.env into local.env, and set up your params',
                obj=settings,
                id='waves.demo.W001', ))
    return errors
