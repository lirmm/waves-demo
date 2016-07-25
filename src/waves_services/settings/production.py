# In production set the environment variable like this:
#    DJANGO_SETTINGS_MODULE=waves.settings.production
from __future__ import unicode_literals
from .base import *             # NOQA
from os import path, makedirs
import errno

import logging.config

# For security and performance reasons, DEBUG is turned off
DEBUG = env.bool('DEBUG')
TEMPLATES[0]['OPTIONS'].update({'debug': DEBUG})

ALLOWED_HOSTS = ['.atgc-montpellier.fr', '193.49.110.17']

vars().update(env.email(backend='django.core.mail.backends.smtp.EmailBackend'))

# Cache the templates in memory for speed-up
loaders = [
    ('django.template.loaders.cached.Loader', [
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    ]),
]

TEMPLATES[0]['OPTIONS'].update({"loaders": loaders})
TEMPLATES[0].update({"APP_DIRS": False})

# Log everything to the logs directory at the top

LOGFILE_ROOT = env('LOG_ROOT_DIR')

if not path.exists(LOGFILE_ROOT):
    try:
        makedirs(LOGFILE_ROOT)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            print "Misconfiguration : waves log dir does not exists !"
            raise

# Reset logging
LOGGING_CONFIG = None
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s [%(pathname)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'waves_log_file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': join(LOGFILE_ROOT, 'waves.log'),
            'formatter': 'verbose',
            'backupCount': 10
        },
        'queue_log_file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': join(LOGFILE_ROOT, 'spool.log'),
            'formatter': 'verbose',
            'backupCount': 10
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['waves_log_file'],
            'propagate': True,
            'level': 'WARNING',
        },
        'waves.queue': {
            'handlers': ['queue_log_file'],
            'level': 'INFO',
        },
        'waves': {
            'handlers': ['waves_log_file'],
            'level': 'INFO',
        }
    }
}

logging.config.dictConfig(LOGGING)
