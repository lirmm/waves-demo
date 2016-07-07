from os import getenv
from os.path import dirname, join
from django.conf import settings

default_app_config = "waves.apps.WavesConfig"

# WAVES Defaults VALUES
settings.WAVES_NOTIFY_RESULTS = getattr(settings, 'WAVES_NOTIFY_RESULTS', True)
settings.WAVES_BASEDIR = getattr(settings, 'WAVES_BASEDIR', dirname(settings.BASE_DIR))
settings.WAVES_SERVICES_EMAIL = getattr(settings, 'WAVES_SERVICES_EMAIL', 'waves@atgc-montpellier.fr')
settings.WAVES_ANONYMOUS_EMAIL = getattr(settings, 'WAVES_ANONYMOUS_EMAIL', 'anonymous@wavesservices-montpellier.fr')
settings.WAVES_DATA_ROOT = getattr(settings, 'WAVES_DATA_ROOT', join(settings.WAVES_BASEDIR, 'data'))
settings.WAVES_JOB_DIR = getattr(settings, 'WAVES_JOB_DIR', join(settings.WAVES_DATA_ROOT, 'jobs'))
settings.WAVES_SAMPLE_DIR = getattr(settings, 'WAVES_SAMPLE_DIR', join(settings.MEDIA_ROOT, 'sample'))
settings.WAVES_CRON_USER = getattr(settings, 'WAVES_CRON_USER', 'cronjob@waves.atgc-montpellier.fr')
settings.WAVES_GALAXY_URL = getattr(settings, 'WAVES_GALAXY_URL', getenv('WAVES_GALAXY_URL', 'http://127.0.0.1'))
settings.WAVES_GALAXY_API_KEY = getattr(settings, 'WAVES_GALAXY_API_KEY',
                                        getenv('WAVES_GALAXY_API_KEY', '806dcbdca2b8bb34f2693cbf318a358e'))
settings.WAVES_GALAXY_PORT = getattr(settings, 'WAVES_GALAXY_PORT', getenv('WAVES_GALAXY_PORT', '8080'))
settings.WAVES_API_TEST_KEY = getattr(settings, 'WAVES_API_TEST_KEY', '806dcbdca2b8bb34f2693cbf318a358e')
settings.WAVES_DRMAA_LIBRARY_PATH = getattr(settings, 'WAVES_DRMAA_LIBRARY_PATH',
                                            getenv('DRMAA_LIBRARY_PATH', '/usr/lib/libdrmaa.so'))
settings.WAVES_SGE_ROOT = getattr(settings, 'WAVES_SGE_ROOT', getenv('SGE_ROOT', '/var/lib/gridengine'))
settings.WAVES_SGE_CELL = getattr(settings, 'WAVES_SGE_CELL', getenv('SGE_CELL', 'default'))
settings.WAVES_DEBUG_STACKTRACE = getattr(settings, 'WAVES_DEBUG_STACKTRACE', False)

settings.WAVES_GROUP_ADMIN = getattr(settings, 'WAVES_GROUP_ADMIN', 'WAVES_ADMIN')
settings.WAVES_GROUP_API = getattr(settings, 'WAVES_GROUP_API', 'WAVES_API_USER')
settings.WAVES_GROUP_USER = getattr(settings, 'WAVES_GROUP_USER', 'WAVES_WEB_USER')

settings.WAVES_FORM_PROCESSOR = getattr(settings, 'WAVES_FORM_PROCESSOR', 'crispy')
settings.DEFAULT_FROM_EMAIL = 'webmaster@waves.atgc-montpellier.fr'

# WAVES DEPENDENCIES DEFAULT VALUES
settings.TABBED_ADMIN_USE_JQUERY_UI = getattr(settings, 'TABBED_ADMIN_USE_JQUERY_UI', False)

settings.CRON_LOGS = getattr(settings, 'CRON_LOGS', '>> %s/spool_log.log' % settings.LOGFILE_ROOT)

settings.CRONTAB_LOCK_JOBS = True

settings.CRONJOBS = getattr(settings, 'CRONJOBS', [
    ('*/1 * * * *', 'waves.managers.cron.treat_queue_jobs'),
])
