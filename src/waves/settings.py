"""
WAVES proprietary optional settings
"""
from __future__ import unicode_literals

import environ
# monkey patch to be sure saga is loaded first (before any logging)
import saga
from os.path import join, dirname
from django.conf import settings

# check if environ has been setup in Django settings.py or initialize an new one
env = getattr(settings, 'env', None)
if env is None:
    env = environ.Env()
env_file_name = getattr(settings, 'WAVES_ENV_FILE', None)
if env_file_name is None:
    env_file_name = join(settings.BASE_DIR, 'waves', 'config', 'waves.env')
environ.Env.read_env(str(env_file_name))


def get_setting(var, cast, default=environ.Env.NOTSET, override=False):
    """
    Get setting var value from possible locations:
     - check in Django base settings.py
     - check in os.env value
     - check if present in 'Waves' env file (possibly defined in WAVES_ENV_FILE settings) if so, set env variable
     - if default, return default value

    :param var: var name to check
    :param cast: var expected type (str, bool, int, etc...) see :ref:https://django-environ.readthedocs.io/
    :param default: default value (if not present may raise Run
    :param override: reset settings var name value (or with 'override' name if provided)
    :return: the setting final value
    """
    # try to get value from settings, then from env, and finally return default
    setting_value = getattr(settings, var, env.get_value(var, cast, default=default))
    if override is True:
        if getattr(settings, var, None) is None:
            setattr(settings, var, setting_value)
    elif override:
        # override if not specified in settings
        setattr(settings, override, setting_value)
    return setting_value


################################
# WAVES Application parameters #
################################
# REGISTRATION
WAVES_REGISTRATION_ALLOWED = get_setting('WAVES_REGISTRATION_ALLOWED', bool, default=True,
                                         override='REGISTRATION_ALLOWED')
WAVES_ACCOUNT_ACTIVATION_DAYS = get_setting('WAVES_ACCOUNT_ACTIVATION_DAYS', int, default=7,
                                            override='ACCOUNT_ACTIVATION_DAYS')
WAVES_BOOTSTRAP_THEME = get_setting('WAVES_BOOTSTRAP_THEME', str, default='flatly', override='BOOTSTRAP_THEME')
# ---- WEB APP ----
# ---- Titles
WAVES_APP_NAME = get_setting('WAVES_APP_NAME', str, default='WAVES')
WAVES_APP_VERBOSE_NAME = get_setting('WAVES_APP_VERBOSE_NAME', str,
                                     default='Web Application for Versatile & Easy bioinformatics Services')
if 'grappelli' in settings.INSTALLED_APPS:
    WAVES_ADMIN_HEADLINE = get_setting('WAVES_ADMIN_HEADLINE', str, default="Waves",
                                       override='GRAPPELLI_ADMIN_HEADLINE')
    WAVES_ADMIN_TITLE = get_setting('WAVES_ADMIN_TITLE', str, default='WAVES Administration',
                                    override='GRAPPELLI_ADMIN_TITLE')
else:
    WAVES_ADMIN_HEADLINE = get_setting('WAVES_ADMIN_HEADLINE', str, default="Waves",
                                       override='ADMIN_HEADLINE')
    WAVES_ADMIN_TITLE = get_setting('WAVES_ADMIN_TITLE', str, default='WAVES Administration',
                                    override='ADMIN_TITLE')

# ---- Form processor (services form generation)
WAVES_FORM_PROCESSOR = get_setting('WAVES_FORM_PROCESSOR', str, default='crispy')
WAVES_TEMPLATE_PACK = get_setting('WAVES_TEMPLATE_PACK', str, default='bootstrap3', override='CRISPY_TEMPLATE_PACK')

# ---- EMAILS ----
# - Set whether user job follow-up emails are globally activated
#   (may be set in back-office for specific service)
WAVES_NOTIFY_RESULTS = get_setting('WAVES_NOTIFY_RESULTS', bool, default=True)
# - Contact emails
WAVES_SERVICES_EMAIL = get_setting('WAVES_SERVICES_EMAIL', str, default='waves@atgc-montpellier.fr')

# ---- WAVES WORKING DIRS ----
# - Base dir for uploaded data and job results
WAVES_DATA_ROOT = get_setting('WAVES_DATA_ROOT', str, default=str(join(dirname(settings.BASE_DIR), 'data')))
# - Jobs working dir (default is relative to WAVES_DATA_ROOT
WAVES_JOB_DIR = get_setting('WAVES_JOB_DIR', str, default=str(join(WAVES_DATA_ROOT, 'jobs')))

# - Uploaded services sample data dir (default is relative to media root)
WAVES_SAMPLE_DIR = get_setting('WAVES_SAMPLE_DIR', str, default=str(join(WAVES_DATA_ROOT, 'sample')))
# - Max uploaded fil size (default is 20Mo)
WAVES_UPLOAD_MAX_SIZE = get_setting('WAVES_UPLOAD_MAX_SIZE', int, 20 * 1024 * 1024)
# - Jobs max retry before abort running
WAVES_JOBS_MAX_RETRY = get_setting('WAVES_JOBS_MAX_RETRY', int, 5)

# ---- QUEUE ----
WAVES_LOG_ROOT = get_setting('WAVES_LOG_ROOT', str, default=join(dirname(settings.BASE_DIR), 'logs'))
WAVES_QUEUE_LOG_LEVEL = get_setting('WAVES_QUEUE_LOG_LEVEL', str, default='WARNING')

# -- Number of days to keep anonymous jobs in database / on disk
WAVES_KEEP_ANONYMOUS_JOBS = get_setting('WAVES_KEEP_ANONYMOUS_JOBS', int, default=30)
# -- Number of days to keep registered user's jobs in database / on disk
WAVES_KEEP_REGISTERED_JOBS = get_setting('WAVES_KEEP_REGISTERED_JOBS', int, default=120)

# ---- TESTS PARAMETERS ----
WAVES_TEST_DEBUG = get_setting('WAVES_TEST_DEBUG', bool, default=False)
# -- Adaptors
WAVES_TEST_DIR = get_setting('WAVES_TEST_DIR', str, default=join(dirname(settings.BASE_DIR) + '/tests/'))
# - Galaxy
WAVES_TEST_GALAXY_URL = get_setting('WAVES_TEST_GALAXY_URL', str, default='127.0.0.1')
WAVES_TEST_GALAXY_API_KEY = get_setting('WAVES_TEST_GALAXY_API_KEY', str, default='your-galaxy-test-api-key')
WAVES_TEST_GALAXY_PORT = get_setting('WAVES_TEST_GALAXY_PORT', str, default='8080')
# -- SGE cluster
WAVES_TEST_SGE_CELL = get_setting('WAVES_TEST_SGE_CELL', str, default='mainqueue')
# - SSH remote user / pass
WAVES_TEST_SSH_HOST = get_setting('WAVES_TEST_SSH_HOST', str, default='127.0.0.1')
WAVES_TEST_SSH_USER_ID = get_setting('WAVES_TEST_SSH_USER_ID', str, default='your-test-ssh-user')
WAVES_TEST_SSH_USER_PASS = get_setting('WAVES_TEST_SSH_USER_PASS', str, default='your-test-ssh-user-pass')
# - SSH remote pub / private key
WAVES_TEST_SSH_PUB_KEY = get_setting('WAVES_TEST_SSH_PUB_KEY', str, default='path-to-ssh-user-public-key')
WAVES_TEST_SSH_PRI_KEY = get_setting('WAVES_TEST_SSH_PRI_KEY', str, default='path-to-ssh-user-private-key')
WAVES_TEST_SSH_PASS_KEY = get_setting('WAVES_TEST_SSH_PASS_KEY', str, default='your-test-ssh-user-key-pass-phrase')

WAVES_ADAPTORS = get_setting('WAVES_ADAPTORS', list,
                             default=['waves.adaptors.local.ShellJobAdaptor', 'waves.adaptors.sge.SGEJobAdaptor',
                                      'waves.adaptors.api.galaxy.GalaxyJobAdaptor'])
