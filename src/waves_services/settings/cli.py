from __future__ import unicode_literals
from .production import *

import logging.config

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

