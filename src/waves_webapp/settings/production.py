from __future__ import unicode_literals

from waves_webapp.settings.base import *             # NOQA
import logging.config

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

DEBUG = False
# Cache the templates in memory for speed-up
loaders = [
    ('django.template.loaders.cached.Loader', [
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    ]),
]
TEMPLATES[0]['OPTIONS'].update({"loaders": loaders})
TEMPLATES[0].update({"APP_DIRS": False})
# # Reset logging
LOGGING_CONFIG = None
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s [%(pathname)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s [%(pathname)s] %(message)s'
        },
    },
    'handlers': {
        'waves_log_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': join(LOG_ROOT, 'waves.log'),
            'formatter': 'verbose',
            'backupCount': 10,
            'maxBytes': 1024*1024*5
        },
    },
    'loggers': {
        'root': {
            'handlers': ['waves_log_file'],
            'propagate': False,
            'level': logging.ERROR,
        },
        'django': {
            'handlers': ['waves_log_file'],
            'level': logging.ERROR,
        },
        'radical.saga': {
            'handlers': ['waves_log_file'],
            'level': logging.ERROR,
        },
        'waves': {
            'handlers': ['waves_log_file'],
            'level': logging.ERROR,
        },
    }
}
logging.config.dictConfig(LOGGING)
