"""
WAVES command line interface default settings configuration
"""
from __future__ import unicode_literals

from .base import *
import logging.config

DEBUG = True
# Reset logging
LOGGING_CONFIG = None
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(levelname)s [%(pathname)s:%(lineno)s] %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        'root': {
            'handlers': ['console'],
            'level': 'ERROR',
        },
        'waves': {
            'handlers': ['console'],
            'level': 'WARNING',
        },
        'radical.saga': {
            'handlers': ['console'],
            'level': 'WARNING',
        },

    }
}
logging.config.dictConfig(LOGGING)

