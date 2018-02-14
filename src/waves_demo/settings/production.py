from __future__ import unicode_literals

from waves_demo.settings.base import *  # NOQA
import environ
import sys
import warnings
WAVES_ENV_FILE = join(dirname(__file__), 'local.prod.env')
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
    'default': env.db(default='sqlite:///' + BASE_DIR + '/waves.prod.sqlite3'),
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

EMAIL_CONFIG = env.email_url('EMAIL_URL', default='smtp://dummyuser@dummyhost:dummypassword@localhost:25')
vars().update(EMAIL_CONFIG)

MANAGERS = env.tuple('MANAGERS', default=[('Marc Chakiachvili', 'marc.chakiachvili@lirmm.fr')])

TEMPLATES[0]['OPTIONS'].update({"loaders": loaders})
TEMPLATES[0].update({"APP_DIRS": False})

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s [%(pathname)s] %(message)s'
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'waves_log_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': join(LOG_ROOT, 'waves.log'),
            'formatter': 'verbose',
            'backupCount': 10,
            'maxBytes': 50000
        },
        'daemon_log_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': join(LOG_ROOT, 'daemon.log'),
            'formatter': 'verbose',
            'backupCount': 10,
            'maxBytes': 50000
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'verbose',
        }
    },
    'loggers': {
        '':{
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        }
    }
}
CONTACT_EMAIL = env.str('CONTACT_EMAIL')
DEFAULT_FROM_EMAIL = 'WAVES <waves-demo@atgc-montpellier.fr>'
WAVES_CORE['ADMIN_EMAIL'] = env.str('ADMIN_EMAIL', 'admin@dummy.fr')
