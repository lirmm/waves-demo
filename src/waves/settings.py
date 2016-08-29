from __future__ import unicode_literals
import environ
from os.path import join, exists
from django.core.urlresolvers import reverse_lazy
from django.conf import settings

# check if environ has been setup in Django settings.py or initialize an new one
env = getattr(settings, 'env', environ.Env())
env_file_name = getattr(settings, 'WAVES_ENV_FILE', 'waves.env')
if not env.bool('WAVES_ENV_LOADED', False):
    # default waves folder structure
    root = environ.Path(__file__) - 3
    def_env_file = join(str(root.path('config')), env_file_name)
    # waves is a dependency for another Django project
    opt_env_file = join(settings.BASE_DIR, env_file_name)
    if exists(def_env_file):
        environ.Env.read_env(str(def_env_file))
    elif exists(opt_env_file):
        environ.Env.read_env(str(opt_env_file))
    else:
        raise RuntimeError(
            'NO WAVES environment found (should be placed either in %s or %s)' % (def_env_file, opt_env_file))


def get_setting(var, cast, default=environ.Env.NOTSET, set_value=False):
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
        set_value: set settings global value

    Returns:
        Any: the setting final value
    """
    # try to get value from settings, then from env, and finally return default
    env_value = env.get_value(var, cast, default=default)
    setting_value = getattr(settings, var, env_value)
    if set_value is True:
        setattr(settings, var, setting_value)
    elif set_value:
        setattr(settings, set_value, setting_value)
    return setting_value


################################
# WAVES Application parameters #
################################
# --------------------------------------------------------
# ----------        OPTIONAL PARAMETERS       ------------
# --------------------------------------------------------
WAVES_DEBUG = get_setting('WAVES_DEBUG', bool, default=False, set_value='DEBUG')
# REGISTRATION
WAVES_REGISTRATION_ALLOWED = get_setting('REGISTRATION_ALLOWED', bool, default=True)
WAVES_ACCOUNT_ACTIVATION_DAYS = get_setting('ACCOUNT_ACTIVATION_DAYS', int, default=7, set_value=True)
WAVES_REGISTRATION_SALT = get_setting('REGISTRATION_SALT', str, set_value=True)

WAVES_BOOTSTRAP_THEME = get_setting('WAVES_BOOTSTRAP_THEME', str, default='darkly', set_value='BOOTSTRAP_THEME')
# ---- WEB APP ----
# ---- Titles
WAVES_APP_NAME = get_setting('WAVES_APP_NAME', str, default='WAVES')
WAVES_APP_VERBOSE_NAME = get_setting('WAVES_APP_VERBOSE_NAME', str,
                                     default='Web Application for Versatile & Easy bioinformatics Services')
if 'grappelli' in settings.INSTALLED_APPS:
    WAVES_ADMIN_HEADLINE = get_setting('WAVES_ADMIN_HEADLINE', str, default="Waves",
                                       set_value='GRAPPELLI_ADMIN_HEADLINE')
    WAVES_ADMIN_TITLE = get_setting('WAVES_ADMIN_TITLE', str, default='WAVES Administration',
                                    set_value='GRAPPELLI_ADMIN_TITLE')
else:
    WAVES_ADMIN_HEADLINE = get_setting('WAVES_ADMIN_HEADLINE', str, default="Waves",
                                       set_value='ADMIN_HEADLINE')
    WAVES_ADMIN_TITLE = get_setting('WAVES_ADMIN_TITLE', str, default='WAVES Administration',
                                    set_value='ADMIN_TITLE')

# ---- Base waves log dir
# WAVES_LOG_ROOT=your-specific-path
# ---- Form processor (services form generation)
WAVES_FORM_PROCESSOR = get_setting('WAVES_FORM_PROCESSOR', str, default='crispy')
# ---- Form css template pack
WAVES_TEMPLATE_PACK = get_setting('WAVES_TEMPLATE_PACK', str, default='bootstrap3', set_value='CRISPY_TEMPLATE_PACK')

# ---- EMAILS ----
# - Set whether user job follow-up emails are globally activated
#   (may be set in back-office for specific service)
WAVES_NOTIFY_RESULTS = get_setting('WAVES_NOTIFY_RESULTS', bool, default=True)
# - Contact emails
WAVES_SERVICES_EMAIL = get_setting('WAVES_SERVICES_EMAIL', str, default='waves@atgc-montpellier.fr')

# ---- WAVES WORKING DIRS ----
# - Base dir for uploaded data and job results
WAVES_DATA_ROOT = get_setting('WAVES_DATA_ROOT', str, default=str(join(settings.ROOT_DIR, 'data')))
# - Jobs working dir (default is relative to WAVES_DATA_ROOT
WAVES_JOB_DIR = get_setting('WAVES_JOB_DIR', str, default=str(join(WAVES_DATA_ROOT, 'jobs')))
# - Uploaded services sample data dir (default is relative to media root)
WAVES_SAMPLE_DIR = get_setting('WAVES_SAMPLE_DIR', str, default=str(join(settings.MEDIA_ROOT, 'sample')))
# - Max uploaded fil size (default is 20Mo)
WAVES_UPLOAD_MAX_SIZE = get_setting('WAVES_UPLOAD_MAX_SIZE', int, 20 * 1024 * 1024)
# - Jobs max retry before abort running
JOBS_MAX_RETRY = get_setting('JOBS_MAX_RETRY', int, 5)
# ---- LOGGING ----
WAVES_LOG_ROOT = get_setting('WAVES_LOG_ROOT', str, default=join(str(settings.ROOT_DIR), 'logs'))

# ---- CRON ----
# -- Job queue timing (default each 5 minutes)
WAVES_QUEUE_CRON = get_setting('WAVES_QUEUE_CRON', str, default='*/5 * * * *')
# -- Purge old job timing (default each day at 00h01)
WAVES_PURGE_CRON = get_setting('WAVES_PURGE_CRON', str, default='1 0 * * *')
# -- Any script or setup to activate before each cron job
WAVES_CRON_TAB_COMMAND_PREFIX = get_setting('CRONTAB_COMMAND_PREFIX', str, default='')
# -- Any script or command suffix to activate after each cron job
WAVES_CRON_TAB_COMMAND_SUFFIX = get_setting('CRONTAB_COMMAND_SUFFIX', str,
                                            default='>> %s' % str(join(WAVES_LOG_ROOT, 'cron.log')))
# -- Number of days to keep anonymous jobs in database / on disk
WAVES_KEEP_ANONYMOUS_JOBS = get_setting('WAVES_KEEP_ANONYMOUS_JOBS', int, default=30)
# -- Number of days to keep registered user's jobs in database / on disk
WAVES_KEEP_REGISTERED_JOBS = get_setting('WAVES_KEEP_REGISTERED_JOBS', int, default=120)

# -- Galaxy server
# Any default galaxy server (in case you manage only one :-))
WAVES_GALAXY_URL = get_setting('WAVES_GALAXY_URL', str, default='http://127.0.0.1')
WAVES_GALAXY_API_KEY = get_setting('WAVES_GALAXY_API_KEY', str, default='mock-api-key')
WAVES_GALAXY_PORT = get_setting('WAVES_GALAXY_PORT', str, default='8080')
# -- SGE cluster
WAVES_SGE_CELL = get_setting('WAVES_SGE_CELL', str, default='all.q')
# -- SSH remote
WAVES_SSH_HOST = get_setting('SSH_HOST', str, default='your-host')
WAVES_SSH_USER_ID = get_setting('SSH_USER_ID', str, default='your-ssh-user')
WAVES_SSH_USER_PASS = get_setting('SSH_USER_PASS', str, default='your-ssh-user-pass')
WAVES_SSH_PUB_KEY = get_setting('SSH_PUB_KEY', str, default='path-ssh-user-public-key')
WAVES_SSH_PRI_KEY = get_setting('SSH_PRI_KEY', str, default='path-ssh-user-private-key')
WAVES_SSH_PASS_KEY = get_setting('SSH_PASS_KEY', str, default='your-ssh-user-key-pass-phrase')

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

# -- OVERRIDE CRON settings CRON
WAVES_QUEUE_CRON_TAB = [(WAVES_QUEUE_CRON, 'waves.managers.cron.treat_queue_jobs'),
                        (WAVES_PURGE_CRON, 'waves.managers.cron.purge_old_jobs')]
# ADD to crontab parameters WAVES cron configuration
if not getattr(settings, 'CRONJOBS', False):
    # In case another config is set add to crontab
    settings.CRONJOBS = WAVES_QUEUE_CRON_TAB
else:
    settings.CRONJOBS += WAVES_QUEUE_CRON_TAB
############################
# Waves dependencies setup #
############################
# ---- DJANGO base parameter overrides
# -- Static waves files check
static_waves_dir = join(settings.BASE_DIR, 'waves', 'static')
if static_waves_dir not in settings.STATICFILES_DIRS:
    # Adds if not present static waves dir to STATICFILES_DIRS
    settings.STATICFILES_DIRS += [static_waves_dir]
WAVES_ALLOWED_HOSTS = get_setting('WAVES_ALLOWED_HOST', list, set_value='ALLOWED_HOSTS')
# ---- CRONTAB (https://github.com/kraiz/django-crontab)
if 'django_crontab' in settings.INSTALLED_APPS:
    settings.CRONTAB_LOCK_JOBS = True
    # TODO manage case when another crontab is already setup in settings (do not override other crontab's elements!)
    settings.CRONTAB_COMMAND_PREFIX = WAVES_CRON_TAB_COMMAND_PREFIX
    settings.CRONTAB_COMMAND_SUFFIX = WAVES_CRON_TAB_COMMAND_SUFFIX
# ---- Grappelli backoffice layout
if 'grappelli' in settings.INSTALLED_APPS:
    # TODO overrides grappelli parameters ?
    pass
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

# TODO override ALLOWED_HOSTS ?
if settings.DEBUG:
    print "loaded settings from waves"
