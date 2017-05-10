""" Development configuration """
from __future__ import unicode_literals

import logging.config

from waves_webapp.settings.base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'dW&j9:DE.tOv!i2)&8Sv>K7"H:l$3mVFYB9)}.Q&d5]C3Ln;*f'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR + '/waves.sample.sqlite3',
    }
}
REGISTRATION_SALT = '4&`cK(7Jza"Nj^1{PN<gtZs5pRaS9'

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
            'format': '[%(levelname)s][%(asctime)s][%(pathname)s:line %(lineno)s][%(name)s.%(funcName)s] - %(message)s',
            'datefmt': "%H:%M:%S"
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
    'root': {
        'handlers': ['console'],
        'propagate': True,
        'level': 'WARNING',
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
    }
}
logging.config.dictConfig(LOGGING)

