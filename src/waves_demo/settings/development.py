""" Development configuration """
from __future__ import unicode_literals

import logging.config

from waves_demo.settings.base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'dW&j9:DE.tOv!i2)&8Sv>K7"H:l$3mVFYB9)}.Q&d5]C3Ln;*f'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR + '/waves_demo.dev.sqlite3',
    }
}
REGISTRATION_SALT = '4&`cK(7Jza"Nj^1{PN<gtZs5pRaS9'
ALLOWED_HOSTS = ["*"]
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
        'daemon_log_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': join(LOG_ROOT, 'daemon.log'),
            'formatter': 'verbose',
            'backupCount': 10,
            'maxBytes': 1024 * 1024 * 5
        },

    },

    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'ERROR',
        },
        'radical.saga': {
            'handlers': ['console'],
            'level': 'ERROR',
        },
        'waves': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'waves.adaptors.galaxy.importers': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False
        },
    }
}
logging.config.dictConfig(LOGGING)

ACCOUNT_ACTIVATION_DAYS = 7

EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = join(BASE_DIR, 'messages')

CONTACT_EMAIL = 'dummy@dummy.host'
DEFAULT_FROM_EMAIL = 'WAVES <waves-demo@atgc-montpellier.fr>'
WAVES_CORE = {
    'ACCOUNT_ACTIVATION_DAYS': 14,
    'APP_NAME': 'WAVES DEMO -DEV-',
    'JOB_LOG_LEVEL': logging.DEBUG,
    'SRV_IMPORT_LOG_LEVEL': logging.DEBUG,
    'ADAPTORS_CLASSES': (
        'demo.adaptors.SshShellAdaptor',
        'demo.adaptors.LocalClusterAdaptor',
        'demo.adaptors.SshKeyShellAdaptor',
        'demo.adaptors.LocalShellAdaptor',
        'demo.adaptors.SshClusterAdaptor',
        'demo.adaptors.SshKeyClusterAdaptor',
        'demo.adaptors.GalaxyJobAdaptor',
    ),
}
