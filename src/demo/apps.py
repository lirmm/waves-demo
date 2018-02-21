# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig
from django.core.checks import Warning, register
from os.path import basename
from os import access, path
import os


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
    from waves.wcore.settings import waves_settings
    if hasattr(settings, "WAVES_ENV_FILE") and basename(settings.WAVES_ENV_FILE) == "local.sample.env":
        errors.append(
            Warning(
                'You are using sample env configuration file',
                hint='Rename local.sample.env into local.env, and set up your params',
                obj=settings,
                id='waves.demo.W001', ))
    for directory in ['DATA_ROOT', 'JOB_BASE_DIR', 'BINARIES_DIR', 'SAMPLE_DIR']:
        if not access(getattr(waves_settings, directory), os.W_OK):
            errors.append(Warning(
                "Directory %s [%s] is not writable by WAVES" % (directory, getattr(waves_settings, directory)),
                hint='Try changing group permission to a group where your user belong',
                obj=waves_settings,
                id="waves.demo.W0002"))
    return errors
