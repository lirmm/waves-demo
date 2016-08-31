from __future__ import unicode_literals

import sys
import logging.config
from .base import *

# DEBUG
THUMBNAIL_DEBUG = DEBUG
TEMPLATES[0]['OPTIONS'].update({'debug': DEBUG})

# Turn off debug while imported by Celery with a workaround
# See http://stackoverflow.com/a/4806384
if "celery" in sys.argv[0]:
    DEBUG = False
# Django Debug Toolbar
INSTALLED_APPS += ('debug_toolbar.apps.DebugToolbarConfig',)


LOGGING_CONFIG = None
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(name)s.%(funcName)s line %(lineno)s %(message)s',
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'root': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'ERROR',
        },
        'django': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'WARNING',
        },
        'waves': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}
logging.config.dictConfig(LOGGING)
