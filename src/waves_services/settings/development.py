from __future__ import unicode_literals

from .base import * # NOQA

import logging.config
DEBUG = True
# Django Debug Toolbar
INSTALLED_APPS += ('debug_toolbar.apps.DebugToolbarConfig',)
# vars().update(env.email(backend='django.core.mail.backends.smtp.EmailBackend'))
LOGGING_CONFIG = None
# logging.config.fileConfig('/home/marc/Documents/sources/waves/config/logging/development.conf')
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(name)s.%(funcName)s line %(lineno)s %(message)s',
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
            'class': 'logging.FileHandler',
            'filename': join(LOG_ROOT, 'spool.log'),
            'formatter': 'verbose',
        },
        'waves_log_file': {
            'class': 'logging.FileHandler',
            'filename': join(LOG_ROOT, 'waves.log'),
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'root': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'ERROR',
        },
        'django': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'WARNING',
        },
        'radical.saga': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'WARNING',
        },
        'waves': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'waves.models.jobs': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'django_crontab': {
            'handlers': ['console'],
            'level': env.str('CRON_LOG_LEVEL', default='INFO')
        },

    }
}
logging.config.dictConfig(LOGGING)
if DEBUG:
    print "loaded settings from dev"