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
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'WARNING',
        },
        'queue': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'waves': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'django_crontab.crontab': {
            'handlers': ['console'],
            'level': 'INFO',
        }
    }
}

logging.config.dictConfig(LOGGING)

