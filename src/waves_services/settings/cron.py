from __future__ import unicode_literals

from .base import *

import logging.config
import sys
# This file is meant only to be used by 'crontab' manage command
import warnings

message = "This file is meant only to be used with and by crontab (django_crontab app)"
if 'django_crontab' not in INSTALLED_APPS:
    warnings.warn('Django crontab app is not installed %s !' % message)
    exit(0)
else:
    if 'crontab' not in sys.argv:
        warnings.warn(message)
        exit(0)

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
            'level': 'WARNING',
        },
        'waves': {
            'level': "INFO",
            'handlers': ['log_file'],
            'propagate': True
        },
        'django_crontab': {
            'level': 'INFO',
            'handlers': ['log_file'],
        },
        'radical.saga': {
            'level': 'INFO',
            'handlers': ['log_file'],
        },

    }
}
logging.config.dictConfig(LOGGING)

