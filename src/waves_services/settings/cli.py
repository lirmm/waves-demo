from __future__ import unicode_literals
from .base import *
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
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'queue_log_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': join(ROOT_DIR, 'logs', 'spool.log'),
            'formatter': 'verbose',
            'maxBytes': 1024*1024*5,
            'backupCount': 10
        },
    },
    'loggers': {
        'root': {
            'handlers': ['queue_log_file'],
            'propagate': False,
            'level': 'WARNING',
        },
        'waves': {
            'handlers': ['queue_log_file'],
            'level': env.str('CRON_LOG_LEVEL', default="INFO"),
            'propagate': False
        },
        'django_crontab': {
            'handlers': ['queue_log_file'],
            'level': env.str('CRON_LOG_LEVEL', default='INFO')
        },
        'radical.saga': {
            'handlers': ['queue_log_file'],
            'propagate': True,
            'level': 'INFO',
        },

    }
}
logging.config.dictConfig(LOGGING)

