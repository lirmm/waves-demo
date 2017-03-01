"""
WAVES proprietary optional settings
These settings may be overridden in your Django main configuration file
"""
from __future__ import unicode_literals

from os.path import join
from django.conf import settings

WAVES_DB_VERSION = '1.1'

WAVES_DATA_ROOT = getattr(settings, 'WAVES_DATA_ROOT', join(settings.MEDIA_ROOT, 'data'))
WAVES_JOB_DIR = getattr(settings, 'WAVES_DATA_ROOT', join(settings.MEDIA_ROOT, 'jobs'))
WAVES_SAMPLE_DIR = join(settings.MEDIA_ROOT, 'samples')
WAVES_UPLOAD_MAX_SIZE = getattr(settings, 'WAVES_UPLOAD_MAX_SIZE', 1024 * 1024 * 10)
