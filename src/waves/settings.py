"""
WAVES proprietary optional settings
These settings may be overridden in your Django main configuration file
"""
from __future__ import unicode_literals

from os.path import join, dirname

from django.conf import settings


def init_setting(var, default=None, override=None):
    """
    Get setting var value from possible locations:
     - check in Django base settings.py
     - if default is set, set settings value
     - return setting value

    :param var: var name to check
    :param default: default value
    :param override: override another app settings value
    :return: the setting final value
    """
    settings_val = getattr(settings, var, None)
    if settings_val is None:
        setattr(settings, var, default)
        settings_val = default
    if override is not None:
        # override another app variable if not specified in settings
        if getattr(settings, override, None) is None:
            setattr(settings, override, settings_val)
    # in any case, register default value to settings
    return settings_val


################################
# WAVES Application parameters #
################################
# REGISTRATION
#: Maximum days account activation link will last
WAVES_ACCOUNT_ACTIVATION_DAYS = init_setting('WAVES_ACCOUNT_ACTIVATION_DAYS', default=7,
                                             override='ACCOUNT_ACTIVATION_DAYS')
#: Selected bootstrap theme
WAVES_BOOTSTRAP_THEME = init_setting('WAVES_BOOTSTRAP_THEME', default='slate', override='BOOTSTRAP_THEME')
# ---- WEB APP ----
# ---- Titles
#: Application default name
WAVES_APP_NAME = init_setting('WAVES_APP_NAME', default='WAVES')
#: Application Verbose name
WAVES_APP_VERBOSE_NAME = init_setting('WAVES_APP_VERBOSE_NAME',
                                      default='Web Application for Versatile & Easy bioinformatics Services')
WAVES_ADMIN_HEADLINE = init_setting('WAVES_ADMIN_HEADLINE', default="Waves", override='ADMIN_HEADLINE')
WAVES_ADMIN_TITLE = init_setting('WAVES_ADMIN_TITLE', default='WAVES Administration', override='ADMIN_TITLE')

# ---- Form processor (services form generation)
#: WAVES form processor
WAVES_FORM_PROCESSOR = init_setting('WAVES_FORM_PROCESSOR', default='crispy')
#: WAVES forms template pack
WAVES_TEMPLATE_PACK = init_setting('WAVES_TEMPLATE_PACK', default='bootstrap3', override='CRISPY_TEMPLATE_PACK')

# ---- EMAILS ----
# - Set whether user job follow-up emails are globally activated
#   (may be set in back-office for specific service)
#: Set whether job states should be notified to end users
WAVES_NOTIFY_RESULTS = init_setting('WAVES_NOTIFY_RESULTS', default=True)
# - Contact emails
#: From email for notification
WAVES_SERVICES_EMAIL = init_setting('WAVES_SERVICES_EMAIL', default='waves@atgc-montpellier.fr')
WAVES_ADMIN_EMAIL = init_setting('WAVES_ADMIN_EMAIL', default='admin@atgc-montpellier.fr')

# ---- WAVES WORKING DIRS ----
# - Base dir for uploaded data and job results
#: WAVES data base dir (store jobs and sample contents)
WAVES_DATA_ROOT = init_setting('WAVES_DATA_ROOT', default=str(join(dirname(settings.BASE_DIR), 'data')))
# - Jobs working dir (default is relative to WAVES_DATA_ROOT
#: WAVES Jobs working dir
WAVES_JOB_DIR = init_setting('WAVES_JOB_DIR', default=str(join(WAVES_DATA_ROOT, 'jobs')))

# - Uploaded services sample data dir (default is relative to media root)
#: WAVES Services sample files dir
WAVES_SAMPLE_DIR = init_setting('WAVES_SAMPLE_DIR', default=str(join(WAVES_DATA_ROOT, 'sample')))
# - Max uploaded fil size (default is 20Mo)
#: Maximum upload file size
WAVES_UPLOAD_MAX_SIZE = init_setting('WAVES_UPLOAD_MAX_SIZE', 20 * 1024 * 1024)
# - Jobs max retry before abort running
#: Maximum retry before job permanently fails
WAVES_JOBS_MAX_RETRY = init_setting('WAVES_JOBS_MAX_RETRY', 5)

# ---- QUEUE ----
#: WAVES log base directory
WAVES_LOG_ROOT = init_setting('WAVES_LOG_ROOT', default=join(dirname(settings.BASE_DIR), 'logs'))
#: WAVES job queue log level
WAVES_QUEUE_LOG_LEVEL = init_setting('WAVES_QUEUE_LOG_LEVEL', default='WARNING')

# -- Number of days to keep anonymous jobs in database / on disk
#: Number of day anonymous jobs should be kept on disk
WAVES_KEEP_ANONYMOUS_JOBS = init_setting('WAVES_KEEP_ANONYMOUS_JOBS', default=30)
# -- Number of days to keep registered user's jobs in database / on disk
#: Number of day registered users jobs should be kept on disk
WAVES_KEEP_REGISTERED_JOBS = init_setting('WAVES_KEEP_REGISTERED_JOBS', default=120)

# ---- TESTS PARAMETERS ----
#: Whether test result should stay on disk after run
WAVES_TEST_DEBUG = init_setting('WAVES_TEST_DEBUG', default=False)
# -- Adaptors
#: WAVES initial data dir for tests
WAVES_TEST_DIR = init_setting('WAVES_TEST_DIR', default=join(dirname(settings.BASE_DIR) + '/tests/'))
# - Galaxy
#: Any Galaxy host defined for tests
WAVES_TEST_GALAXY_URL = init_setting('WAVES_TEST_GALAXY_URL', default='https://use.galaxy.org')
#: Galaxy host api_key tests
WAVES_TEST_GALAXY_API_KEY = init_setting('WAVES_TEST_GALAXY_API_KEY', default='your-galaxy-test-waves_api-key')
#: Galaxy host port for tests
WAVES_TEST_GALAXY_PORT = init_setting('WAVES_TEST_GALAXY_PORT', default=None)
# -- SGE cluster
#: SGE cell default queue for tests
WAVES_TEST_SGE_CELL = init_setting('WAVES_TEST_SGE_CELL', default='mainqueue')
# - SSH remote user / pass
#: TEST SSH host
WAVES_TEST_SSH_HOST = init_setting('WAVES_TEST_SSH_HOST', default='127.0.0.1')
#: TEST SSH user id
WAVES_TEST_SSH_USER_ID = init_setting('WAVES_TEST_SSH_USER_ID', default='your-test-ssh-user')
#: TEST SSH user pass (encoded with)
WAVES_TEST_SSH_USER_PASS = init_setting('WAVES_TEST_SSH_USER_PASS', default='your-test-ssh-user-pass')
# - SSH remote pub / private key
#: TEST SSH public key path for tests
WAVES_TEST_SSH_PUB_KEY = init_setting('WAVES_TEST_SSH_PUB_KEY', default='path-to-ssh-user-public-key')
#: TEST SSH private key path for tests
WAVES_TEST_SSH_PRI_KEY = init_setting('WAVES_TEST_SSH_PRI_KEY', default='path-to-ssh-user-private-key')
#: TEST SSH passphrade for tests
#: python command :
WAVES_TEST_SSH_PASS_KEY = init_setting('WAVES_TEST_SSH_PASS_KEY', default='your-test-ssh-user-key-pass-phrase')

#: Set whether GALAY histories should be erased after job completion
WAVES_DEBUG_GALAXY = init_setting('WAVES_DEBUG_GALAXY', default=False)
WAVES_DB_VERSION = '1.0'
