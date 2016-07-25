from os import getenv
from os.path import dirname, join
from django.conf import settings

default_app_config = "waves.apps.WavesConfig"


def _get_setting_or_env(var, cast, default):
    # try to get value from settings, then from env, and finally return default
    return getattr(settings, var, settings.ENV.get_value(var, cast, default=default))

# WAVES Defaults VALUES
settings.WAVES_APP_NAME = _get_setting_or_env('WAVES_APP_NAME', str, "WAVES")
settings.WAVES_NOTIFY_RESULTS = _get_setting_or_env('WAVES_NOTIFY_RESULTS', bool, True)
settings.WAVES_BASEDIR = _get_setting_or_env('WAVES_BASEDIR', str, dirname(settings.BASE_DIR))
settings.WAVES_SERVICES_EMAIL = _get_setting_or_env('WAVES_SERVICES_EMAIL', str, 'waves@atgc-montpellier.fr')
settings.WAVES_DATA_ROOT = _get_setting_or_env('WAVES_DATA_ROOT', str, join(settings.WAVES_BASEDIR, 'data'))
settings.WAVES_JOB_DIR = _get_setting_or_env('WAVES_JOB_DIR', str, join(settings.WAVES_DATA_ROOT, 'jobs'))
settings.WAVES_SAMPLE_DIR = _get_setting_or_env('WAVES_SAMPLE_DIR', str, join(settings.MEDIA_ROOT, 'sample'))
settings.WAVES_GALAXY_URL = _get_setting_or_env('WAVES_GALAXY_URL', str, 'http://127.0.0.1')
settings.WAVES_GALAXY_API_KEY = _get_setting_or_env('WAVES_GALAXY_API_KEY', str, '806dcbdca2b8bb34f2693cbf318a358e')
settings.WAVES_GALAXY_PORT = _get_setting_or_env('WAVES_GALAXY_PORT', str, '8080')
settings.WAVES_API_TEST_KEY = _get_setting_or_env('WAVES_API_TEST_KEY', str, '806dcbdca2b8bb34f2693cbf318a358e')
settings.WAVES_DRMAA_LIBRARY_PATH = _get_setting_or_env('WAVES_DRMAA_LIBRARY_PATH', str, getenv('DRMAA_LIBRARY_PATH',
                                                                                                '/usr/lib/libdrmaa.so'))
settings.WAVES_SGE_CELL = _get_setting_or_env('WAVES_SGE_CELL', str, 'mainqueue')
settings.WAVES_GROUP_ADMIN = _get_setting_or_env('WAVES_GROUP_ADMIN', str, 'WAVES_ADMIN')
settings.WAVES_GROUP_API = _get_setting_or_env('WAVES_GROUP_API', str, 'WAVES_API_USER')
settings.WAVES_GROUP_USER = _get_setting_or_env('WAVES_GROUP_USER', str, 'WAVES_WEB_USER')
settings.WAVES_FORM_PROCESSOR = _get_setting_or_env('WAVES_FORM_PROCESSOR', str, 'crispy')

# WAVES dependencies set up
settings.DEFAULT_FROM_EMAIL = _get_setting_or_env('DEFAULT_FROM_EMAIL', str, 'webmaster@waves.atgc-montpellier.fr')
settings.TABBED_ADMIN_USE_JQUERY_UI = _get_setting_or_env('TABBED_ADMIN_USE_JQUERY_UI', bool, False)
settings.CRON_LOGS = _get_setting_or_env('CRON_LOGS', str, '>> %s/spool_log.log' % settings.LOGFILE_ROOT)
settings.CRONTAB_LOCK_JOBS = True
settings.WAVES_UPLOAD_MAX_SIZE = _get_setting_or_env('WAVES_UPLOAD_MAX_SIZE', int, 20*1024*1024)
settings.CRONJOBS = _get_setting_or_env('CRONJOBS', list, [('*/1 * * * *', 'waves.managers.cron.treat_queue_jobs'),])
