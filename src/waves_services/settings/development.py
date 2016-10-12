from __future__ import unicode_literals

import sys
import logging.config
from .base import *

DEBUG = True
DEBUG404 = True
# DEBUG
THUMBNAIL_DEBUG = DEBUG
TEMPLATES[0]['OPTIONS'].update({'debug': DEBUG})

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
            'level': logging.ERROR,
        },
        'django': {
            'handlers': ['console'],
            'propagate': False,
            'level': logging.WARNING,
        },
        'waves': {
            'handlers': ['console'],
            'level': logging.DEBUG,
            'propagate': False,
        },
    }
}
logging.config.dictConfig(LOGGING)
