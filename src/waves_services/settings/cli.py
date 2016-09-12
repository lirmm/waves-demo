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
            'level': ROOT_LOG_LEVEL,
        },
        'waves': {
            'handlers': ['console'],
            'level': WAVES_LOG_LEVEL,
        },
        'radical.saga': {
            'handlers': ['console'],
            'level': SAGA_LOG_LEVEL,
        },

    }
}
logging.config.dictConfig(LOGGING)

