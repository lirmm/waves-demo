""" Development configuration """
from __future__ import unicode_literals


import logging.config
from waves_webapp.settings.base import *

DEBUG = True
DEBUG404 = True
# DEBUG
THUMBNAIL_DEBUG = DEBUG
TEMPLATES[0]['OPTIONS'].update({'debug': DEBUG})

LOGGING_CONFIG = None
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[%(levelname)s][%(name)s.%(funcName)s:line %(lineno)s] - %(message)s',
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '[%(levelname)s] - %(message)s'
        },
        'trace': {
            'format': '%(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'waves_daemon': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': join(LOG_ROOT, 'daemon.log'),
            'formatter': 'verbose',
            'backupCount': 10,
            'maxBytes': 1024 * 2
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'WARNING',
        },
        'waves': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'waves.management': {
            'handlers': ['waves_daemon'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'waves_adaptors': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        }
    }
}
logging.config.dictConfig(LOGGING)
REST_FRAMEWORK['DEFAULT_PERMISSION_CLASSES'] = [
    'rest_framework.permissions.AllowAny',
]
REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'] = []
