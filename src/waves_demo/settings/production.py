from __future__ import unicode_literals

from waves_demo.settings.base import *  # NOQA
import environ
import sys
import warnings
import saga
import logging.config

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
    'default': env.db(default='sqlite:///' + BASE_DIR + '/waves.prod.sqlite3'),
}
# patch to use in memory database for testing
if 'test' in sys.argv:
    DATABASES['default']['ENGINE'] = 'django.db.backends.sqlite3'

REGISTRATION_SALT = env.str('REGISTRATION_SALT')

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

CORS_ORIGIN_WHITELIST = ('atgc-montpellier.fr',)
# Cache the templates in memory for speed-up
loaders = [
    ('django.template.loaders.cached.Loader', [
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    ]),
]

EMAIL_CONFIG = env.email_url('EMAIL_URL', default='smtp://dummyuser@dummyhost:dummypassword@localhost:25')
vars().update(EMAIL_CONFIG)

MANAGERS = env.tuple('MANAGERS', default=[('Vincent Lefort', 'vincent.lefort@lirmm.fr')])

TEMPLATES[0]['OPTIONS'].update({"loaders": loaders})
TEMPLATES[0].update({"APP_DIRS": False})
LOGGING_CONFIG = None

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
        'root': {
            'handlers': ['waves_log_file'],
            'propagate': False,
            'level': 'ERROR',
        },
        'django': {
            'handlers': ['waves_log_file'],
            'level': 'ERROR',
        },
        'radical.saga': {
            'handlers': ['waves_log_file'],
            'level': 'WARNING',
        },
        'waves': {
            'handlers': ['waves_log_file'],
            'level': 'WARNING',
        },

    }
}
logging.config.dictConfig(LOGGING)

# EMAILS
DEFAULT_FROM_EMAIL = 'WAVES <waves-demo@atgc-montpellier.fr>'
CONTACT_EMAIL = env.str('CONTACT_EMAIL', DEFAULT_FROM_EMAIL)

# WAVES
WAVES_CORE = {
    'ACCOUNT_ACTIVATION_DAYS': 14,
    'ADMIN_EMAIL': env.str('ADMIN_EMAIL', 'admin@waves.atgc-montpellier.fr'),
    'DATA_ROOT': env.str('WAVES_DATA_ROOT', join(BASE_DIR, 'data')),
    'JOB_BASE_DIR': env.str('WAVES_JOB_BASE_DIR', join(BASE_DIR, 'data', 'jobs')),
    'BINARIES_DIR': env.str('WAVES_BINARIES_DIR', join(BASE_DIR, 'data', 'bin')),
    'SAMPLE_DIR': env.str('WAVES_SAMPLE_DIR', join(MEDIA_ROOT, 'data', 'sample')),
    'KEEP_ANONYMOUS_JOBS': 2,
    'KEEP_REGISTERED_JOBS': 2,
    'ALLOW_JOB_SUBMISSION': True,
    'APP_NAME': 'WAVES DEMO',
    'SERVICES_EMAIL': 'contact@atgc-montpellier.fr',
    'ADAPTORS_CLASSES': (
        'demo.adaptors.SshShellAdaptor',
        'demo.adaptors.LocalClusterAdaptor',
        'demo.adaptors.SshKeyShellAdaptor',
        'demo.adaptors.LocalShellAdaptor',
        'demo.adaptors.SshClusterAdaptor',
        'demo.adaptors.SshKeyClusterAdaptor',
        'demo.adaptors.GalaxyJobAdaptor',
    ),
}

REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'] = (
    'rest_framework.authentication.TokenAuthentication',
    'rest_framework.authentication.BasicAuthentication',
    'rest_framework.authentication.SessionAuthentication',
)
