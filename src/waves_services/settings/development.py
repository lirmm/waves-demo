from __future__ import unicode_literals

from .base import * # NOQA
import sys
import os
import logging.config
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
TEMPLATES[0]['OPTIONS'].update({'debug': True})

# Turn off debug while imported by Celery with a workaround
# See http://stackoverflow.com/a/4806384
if "celery" in sys.argv[0]:
    DEBUG = False

# Django Debug Toolbar
INSTALLED_APPS += ('debug_toolbar.apps.DebugToolbarConfig',)

# Show emails to console in DEBUG mode
#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
vars().update(env.email(backend='django.core.mail.backends.smtp.EmailBackend'))

# Show thumbnail generation errors
THUMBNAIL_DEBUG = True

CRISPY_FAIL_SILENTLY = not DEBUG
LOGFILE_ROOT = join(str(root.path()), 'logs')
LOGGING_CONFIG = None
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
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'INFO',
        },
        'waves': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'job_queue': {
            'handlers': ['console'],
            'level': 'DEBUG',
        }
    }
}

logging.config.dictConfig(LOGGING)
# ADDED restriction to host
ALLOWED_HOSTS = [
    '127.0.0.1',
]
