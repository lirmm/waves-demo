from __future__ import unicode_literals

import environ
from os.path import join
from django.conf import settings

# check if environ has been setup in Django settings.py or initialize an new one
env = getattr(settings, 'env', environ.Env())
if not env.bool('WAVES_ENV_LOADED', False):
    # If waves.env has already been loaded (if all setup is done in any other environment configuration
    # default waves folder structure
    env_file_name = getattr(settings, 'WAVES_ENV_FILE', join(settings.BASE_DIR, 'waves', 'config', 'waves.env'))
    environ.Env.read_env(str(env_file_name))


def get_setting(var, cast, default=environ.Env.NOTSET, override=False):
    """
    Get setting var value from possible locations:
    - check in Django base settings.py
    - check in os.env value
    - check if present in 'Waves' env file (possibly defined in WAVES_ENV_FILE settings) if so, set env variable
    - if default, return default value
    Returns:
        Any
    Args:
        var: var name to check
        cast: var expected type (str, bool, int, etc...) @see: https://django-environ.readthedocs.io/
        default: default value (if not present may raise Run
        override: reset settings var name value (or with 'override' name if provided)
    Returns:
        Any: the setting final value
    """
    # try to get value from settings, then from env, and finally return default
    setting_value = getattr(settings, var, env.get_value(var, cast, default=default))
    if override is True:
        setattr(settings, var, setting_value)
    elif override:
        if getattr(settings, override, None) is None:
            # override if not specified in settings
            setattr(settings, override, setting_value)
    return setting_value


################################
# WAVES Application parameters #
################################
# --------------------------------------------------------
# ----------        OPTIONAL PARAMETERS       ------------
# --------------------------------------------------------
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
WAVES_DATA_ROOT = get_setting('WAVES_DATA_ROOT', str, default=str(join(settings.BASE_DIR, 'data')))
# - Jobs working dir (default is relative to WAVES_DATA_ROOT
WAVES_JOB_DIR = get_setting('WAVES_JOB_DIR', str, default=str(join(WAVES_DATA_ROOT, 'jobs')))
# - Uploaded services sample data dir (default is relative to media root)
WAVES_SAMPLE_DIR = get_setting('WAVES_SAMPLE_DIR', str, default=str(join(settings.MEDIA_ROOT, 'sample')))
# - Max uploaded fil size (default is 20Mo)
WAVES_UPLOAD_MAX_SIZE = get_setting('WAVES_UPLOAD_MAX_SIZE', int, 20 * 1024 * 1024, override='')
# - Jobs max retry before abort running
WAVES_JOBS_MAX_RETRY = get_setting('WAVES_JOBS_MAX_RETRY', int, 5)

# ---- CRON ----
# ---- LOGGING ----
WAVES_LOG_ROOT = get_setting('WAVES_LOG_ROOT', str, default=join(str(settings.BASE_DIR), 'logs'), override='LOG_ROOT')

# -- Galaxy server
# Any default galaxy server (in case you manage only one :-))
WAVES_GALAXY_URL = get_setting('WAVES_GALAXY_URL', str, default='http://127.0.0.1')
WAVES_GALAXY_API_KEY = get_setting('WAVES_GALAXY_API_KEY', str, default='mock-api-key')
WAVES_GALAXY_PORT = get_setting('WAVES_GALAXY_PORT', str, default='8080')
# -- SGE cluster
WAVES_SGE_CELL = get_setting('WAVES_SGE_CELL', str, default='all.q')
# -- SSH remote
WAVES_SSH_HOST = get_setting('WAVES_SSH_HOST', str, default='your-host')
WAVES_SSH_USER_ID = get_setting('WAVES_SSH_USER_ID', str, default='your-ssh-user')
WAVES_SSH_USER_PASS = get_setting('WAVES_SSH_USER_PASS', str, default='your-ssh-user-pass')
WAVES_SSH_PUB_KEY = get_setting('WAVES_SSH_PUB_KEY', str, default='path-ssh-user-public-key')
WAVES_SSH_PRI_KEY = get_setting('WAVES_SSH_PRI_KEY', str, default='path-ssh-user-private-key')
WAVES_SSH_PASS_KEY = get_setting('WAVES_SSH_PASS_KEY', str, default='your-ssh-user-key-pass-phrase')

# ---- TESTS PARAMETERS ----
# -- Adaptors
# - Galaxy
WAVES_TEST_GALAXY_URL = get_setting('WAVES_TEST_GALAXY_URL', str, default='your-galaxy-test-host')
WAVES_TEST_GALAXY_API_KEY = get_setting('WAVES_TEST_GALAXY_API_KEY', str, default='your-galaxy-test-api-key')
WAVES_TEST_GALAXY_PORT = get_setting('WAVES_TEST_GALAXY_PORT', str, default='your-galaxy-test-port')
# -- SGE cluster
WAVES_TEST_SGE_CELL = get_setting('WAVES_TEST_SGE_CELL', str, default=WAVES_SGE_CELL)
# - SSH remote
WAVES_TEST_SSH_HOST = get_setting('WAVES_TEST_SSH_HOST', str, default='your-test-host')
WAVES_TEST_SSH_USER_ID = get_setting('WAVES_TEST_SSH_USER_ID', str, default='your-test-ssh-user')
WAVES_TEST_SSH_USER_PASS = get_setting('WAVES_TEST_SSH_USER_PASS', str, default='your-test-ssh-user-pass')
WAVES_TEST_SSH_PUB_KEY = get_setting('WAVES_TEST_SSH_PUB_KEY', str, default='path-to-ssh-user-public-key')
WAVES_TEST_SSH_PRI_KEY = get_setting('WAVES_TEST_SSH_PRI_KEY', str, default='path-to-ssh-user-private-key')
WAVES_TEST_SSH_PASS_KEY = get_setting('WAVES_TEST_SSH_PASS_KEY', str, default='your-test-ssh-user-key-pass-phrase')

######################################
# Waves dependencies mandatory setup #
######################################
# TODO ADD 'WAVES_USE_DEDICATED_DB' bool parameter and if configured, setup db accordingly to WAVES_DEDICATED_DB_URL
# TODO potentially process WAVES_ALLOWED_HOSTS
# Add template
# ---- DEPENDENCIES parameter overrides
# FILE UPLOAD_HANDLER
upload_handler = getattr(settings, 'FILE_UPLOAD_HANDLERS', None)
if upload_handler is None:
    settings.FILE_UPLOAD_HANDLERS = ["django.core.files.uploadhandler.TemporaryFileUploadHandler"]

# ---- CRONTAB (https://github.com/kraiz/django-crontab)
if 'django_crontab' in settings.INSTALLED_APPS:
    # -- OVERRIDE CRON settings CRON
    # -- Job queue timing (default each 5 minutes)
    WAVES_QUEUE_CRON = get_setting('WAVES_QUEUE_CRON', str, default='*/1 * * * *')
    # -- Purge old job timing (default each day at 00h01)
    WAVES_PURGE_CRON = get_setting('WAVES_PURGE_CRON', str, default='1 0 * * *')
    # -- Any script or setup to activate before each cron job
    WAVES_CRON_TAB_PREFIX = get_setting('WAVES_CRONTAB_COMMAND_PREFIX', str, default='',
                                        override='CRONTAB_COMMAND_PREFIX')
    # -- Any script or command suffix to activate after each cron job
    WAVES_CRON_TAB_SUFFIX = get_setting('WAVES_CRONTAB_COMMAND_SUFFIX', str,
                                        default='2>&1',
                                        override='CRONTAB_COMMAND_SUFFIX')
    # -- Number of days to keep anonymous jobs in database / on disk
    WAVES_KEEP_ANONYMOUS_JOBS = get_setting('WAVES_KEEP_ANONYMOUS_JOBS', int, default=30)
    # -- Number of days to keep registered user's jobs in database / on disk
    WAVES_KEEP_REGISTERED_JOBS = get_setting('WAVES_KEEP_REGISTERED_JOBS', int, default=120)
    WAVES_QUEUE_CRON_TAB = [(WAVES_QUEUE_CRON, 'waves.managers.cron.treat_queue_jobs'),
                            (WAVES_PURGE_CRON, 'waves.managers.cron.purge_old_jobs')]
    # ADD to crontab parameters WAVES cron configuration
    if not getattr(settings, 'CRONJOBS', False):
        # In case another config is set add to crontab
        settings.CRONJOBS = WAVES_QUEUE_CRON_TAB
    else:
        settings.CRONJOBS += WAVES_QUEUE_CRON_TAB
    # WAVES need to lock cron tab jobs execution
    settings.CRONTAB_LOCK_JOBS = True
    settings.CRONTAB_DJANGO_SETTINGS_MODULE = 'waves_services.settings.cron'


# ---- Django REST Framework configuration updates
if 'rest_framework' in settings.INSTALLED_APPS:
    # Update authentication classes for Rest API with dedicated Waves one
    # For others parameters see 'http://www.django-rest-framework.org/api-guide/settings/'
    from rest_framework.settings import api_settings
    import waves.api.authentication.auth

    if waves.api.authentication.auth.WavesAPI_KeyAuthBackend not in api_settings.DEFAULT_AUTHENTICATION_CLASSES:
        current_auths = set(api_settings.DEFAULT_AUTHENTICATION_CLASSES)
        current_auths.update([waves.api.authentication.auth.WavesAPI_KeyAuthBackend])
        api_settings.DEFAULT_AUTHENTICATION_CLASSES = tuple(current_auths)


