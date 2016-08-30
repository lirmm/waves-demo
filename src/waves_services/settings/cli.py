from __future__ import unicode_literals

import logging.config
from .base import * # NOQA


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
            'level': 'WARNING',
        },
        'waves': {
            'handlers': ['console'],
            'level': "INFO",
        },
        'radical.saga': {
            'handlers': ['console'],
            'level': 'INFO',
        },

    }
}
logging.config.dictConfig(LOGGING)

