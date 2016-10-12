from __future__ import unicode_literals

from .base import *

import logging.config
import sys
# This file is meant only to be used by 'crontab' manage command
import warnings

DEBUG = False
# Reset logging
LOGGING_CONFIG = None
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s [%(pathname)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
    },
    'handlers': {
        'log_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': join(LOG_ROOT, 'queue.log'),
            'formatter': 'verbose',
            'maxBytes': 1024*1024*5,
            'backupCount': 10
        },
    },
    'loggers': {
        'root': {
            'handlers': ['log_file'],
            'level': logging.ERROR,
        },
        'waves': {
            'level': logging.WARNING,
            'handlers': ['log_file'],
            'propagate': True
        },
        'waves.daemon': {
            'level': logging.WARNING,
            'handlers': ['log_file'],
        },
        'radical.saga': {
            'level': logging.WARNING,
            'handlers': ['log_file'],
        },

    }
}
logging.config.dictConfig(LOGGING)

