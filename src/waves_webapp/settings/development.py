from __future__ import unicode_literals

import logging.config

from waves_webapp.settings.base import *
DEBUG = True
DEBUG404 = True
# DEBUG
THUMBNAIL_DEBUG = DEBUG
TEMPLATES[0]['OPTIONS'].update({'debug': DEBUG})

# Django Debug Toolbar
INSTALLED_APPS += ('debug_toolbar.apps.DebugToolbarConfig',)
MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)
# LOGGING_CONFIG = None
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[%(levelname)s][%(name)s.%(funcName)s:line %(lineno)s] - %(message)s',
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '[%(levelname)s] - %(message)s'
        },
        'trace': {
            'format': '%(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'waves_daemon': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': join(LOG_ROOT, 'wavesdaemon.log'),
            'formatter': 'verbose',
            'backupCount': 10,
            'maxBytes': 1024 * 1024 * 5
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'WARNING',
        },
        'waves': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'waves.management': {
            'handlers': ['waves_daemon'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'waves_adaptors': {
            'handlers': ['waves_daemon'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'waves_addons': {
            'handlers': ['waves_daemon'],
            'level': 'DEBUG',
            'propagate': False,
        }
    }
}
logging.config.dictConfig(LOGGING)
# - Galaxy
WAVES_TEST_GALAXY_URL = env.str('WAVES_TEST_GALAXY_URL', default='127.0.0.1')
WAVES_TEST_GALAXY_API_KEY = env.str('WAVES_TEST_GALAXY_API_KEY', default='your-galaxy-test-waves_api-key')
WAVES_TEST_GALAXY_PORT = None
WAVES_QUEUE_LOG_LEVEL = 'DEBUG'
WAVES_DEBUG_GALAXY=True
# -- SGE cluster
WAVES_TEST_SGE_CELL = env.str('WAVES_TEST_SGE_CELL', default='mainqueue')
# - SSH remote user / pass
WAVES_TEST_SSH_HOST = env.str('WAVES_TEST_SSH_HOST', default='127.0.0.1')
WAVES_TEST_SSH_USER_ID = env.str('WAVES_TEST_SSH_USER_ID', default='your-test-ssh-user')
WAVES_TEST_SSH_USER_PASS = env.str('WAVES_TEST_SSH_USER_PASS', default='your-test-ssh-user-pass')
# - SSH remote pub / private key
WAVES_TEST_SSH_PUB_KEY = env.str('WAVES_TEST_SSH_PUB_KEY', default='path-to-ssh-user-public-key')
WAVES_TEST_SSH_PRI_KEY = env.str('WAVES_TEST_SSH_PRI_KEY', default='path-to-ssh-user-private-key')
WAVES_TEST_SSH_PASS_KEY = env.str('WAVES_TEST_SSH_PASS_KEY', default='your-test-ssh-user-key-pass-phrase')

REST_FRAMEWORK['DEFAULT_PERMISSION_CLASSES'] = [
    'rest_framework.permissions.AllowAny',
]
REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'] = []
