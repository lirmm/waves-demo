from __future__ import unicode_literals

from waves_demo.settings.base import *             # NOQA
import logging.config
import environ
import sys
import warnings

WAVES_ENV_FILE = join(dirname(__file__), 'local.env')
if not isfile(WAVES_ENV_FILE):
    WAVES_ENV_FILE = join(dirname(__file__), 'local.sample.env')


# Django main environment file (issued from local.en
env = environ.Env()
environ.Env.read_env(WAVES_ENV_FILE)
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str('SECRET_KEY')
DEBUG = env.bool('DEBUG', False)

# DATABASE configuration
DATABASES = {
    'default': env.db(default='sqlite:///' + BASE_DIR + '/waves.sample.sqlite3'),
}
# patch to use in memory database for testing
if 'test' in sys.argv:
    DATABASES['default']['ENGINE'] = 'django.db.backends.sqlite3'

REGISTRATION_SALT = env.str('REGISTRATION_SALT')

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

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
        'daemon_log_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': join(LOG_ROOT, 'daemon.log'),
            'formatter': 'verbose',
            'backupCount': 10,
            'maxBytes': 1024*1024*5
        },
    },
    'loggers': {
        'django': {
            'handlers': ['waves_log_file'],
            'level': 'ERROR',
        },
        'radical.saga': {
            'handlers': ['waves_log_file'],
            'level': 'ERROR',
        },
        'waves': {
            'handlers': ['waves_log_file'],
            'level': 'ERROR',
        },
        'waves.daemon': {
            'handlers': ['waves_log_file'],
            'level': 'DEBUG',
        },
    }
}
logging.config.dictConfig(LOGGING)