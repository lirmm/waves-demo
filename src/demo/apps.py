# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from os import access, W_OK
from os.path import basename

from django.apps import AppConfig
from django.core.checks import Warning, register, Error


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
    log_dir = getattr(settings, 'LOG_ROOT', None)
    if log_dir is None:
        errors.append(Error(
            "Log directory [%s] does not exists " % log_dir,
            hint='Create this directory with group permission for your WAVES daemon system user',
            obj=settings,
            id="waves.wcore.E004"))
    elif not access(log_dir, W_OK):
        errors.append(Warning(
            "Log directory [%s] is not writable by WAVES" % log_dir,
            hint='Try changing group permission to a group where your user belong',
            obj=settings,
            id="waves.wcore.W001"))
    return errors
