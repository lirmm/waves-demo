from django.conf import settings
from django.apps import AppConfig
from os.path import join, dirname
from bootstrap_themes import list_themes

WAVES_CONSTANCE_CONFIG = {
    'WAVES_ACCOUNT_ACTIVATION_DAYS': (7, 'Number of days before activation is kept available'),
    'WAVES_BOOTSTRAP_THEME': ('slate', 'Bootstrap theme for front end', 'select_theme'),
    'WAVES_APP_NAME': ('WAVES', 'Application name'),
    'WAVES_SITE_MAINTENANCE': (False, 'Site in Maintenance'),
    'WAVES_ALLOW_JOB_SUBMISSION': (True, 'Disable job submission (globally)'),
    'WAVES_APP_VERBOSE_NAME': ('Web Application for Versatile & Easy bioinformatics Services',
                               'Application verbose name'),
    'WAVES_ADMIN_HEADLINE': ("Waves", 'Administration headline'),
    'WAVES_ADMIN_TITLE': ('WAVES Administration', 'Administration title'),
    'WAVES_NOTIFY_RESULTS': (True, 'Notify results to clients'),
    'WAVES_SERVICES_EMAIL': ('waves@atgc-montpellier.fr', 'From email for notification'),
    'WAVES_ADMIN_EMAIL': ('admin@atgc-montpellier.fr', 'Waves admin email'),
    'WAVES_DATA_ROOT': (join(dirname(settings.BASE_DIR), 'data'), 'Data root dir'),
    'WAVES_JOB_DIR': (join(dirname(settings.BASE_DIR), 'data', 'jobs'), 'Job working base dir'),
    'WAVES_SAMPLE_DIR': (join(dirname(settings.BASE_DIR), 'data', 'sample'), 'Sample directory'),
    'WAVES_UPLOAD_MAX_SIZE': (1024 * 1024, 'Max uploaded file size'),
    'WAVES_JOBS_MAX_RETRY': (5, 'Default retry for failing jobs'),
    'WAVES_LOG_ROOT': (join(dirname(settings.BASE_DIR), 'logs'), 'Log directory'),
    'WAVES_KEEP_ANONYMOUS_JOBS': (30, 'Number of day to keep anonymous jobs data'),
    'WAVES_KEEP_REGISTERED_JOBS': (120, 'Number of day to keep registered users jobs data'),
}

WAVES_CONSTANCE_ADDITIONAL_FIELDS = {
    'select_theme': ['django.forms.fields.ChoiceField', {
        'widget': 'django.forms.Select',
        'choices': list_themes()
    }],
}

BASE_CONSTANCE_CONFIG = getattr(settings, 'CONSTANCE_CONFIG', {})
BASE_CONSTANCE_CONFIG.update(WAVES_CONSTANCE_CONFIG)
BASE_CONSTANCE_ADDITIONAL_FIELDS = getattr(settings, 'CONSTANCE_ADDITIONAL_FIELDS', {})
BASE_CONSTANCE_ADDITIONAL_FIELDS.update(WAVES_CONSTANCE_ADDITIONAL_FIELDS)
WAVES_CONSTANCE_CONFIG_FIELDSETS = {
    'General Options': ('WAVES_ACCOUNT_ACTIVATION_DAYS', 'WAVES_NOTIFY_RESULTS', 'WAVES_SERVICES_EMAIL'),
    'Front Options': ('WAVES_BOOTSTRAP_THEME', 'WAVES_APP_NAME', 'WAVES_APP_VERBOSE_NAME', 'WAVES_SITE_MAINTENANCE'),
    'Admin Options': ('WAVES_ADMIN_HEADLINE', 'WAVES_ADMIN_TITLE', 'WAVES_APP_VERBOSE_NAME', 'WAVES_ADMIN_EMAIL'),
    'Disk Options': ('WAVES_DATA_ROOT', 'WAVES_JOB_DIR', 'WAVES_SAMPLE_DIR', 'WAVES_LOG_ROOT'),
    'Job Options': ('WAVES_ALLOW_JOB_SUBMISSION', 'WAVES_UPLOAD_MAX_SIZE', 'WAVES_JOBS_MAX_RETRY', 'WAVES_KEEP_ANONYMOUS_JOBS', 'WAVES_KEEP_REGISTERED_JOBS'),
}
settings.CONSTANCE_CONFIG = BASE_CONSTANCE_CONFIG
settings.CONSTANCE_ADDITIONAL_FIELDS = BASE_CONSTANCE_ADDITIONAL_FIELDS
settings.CONSTANCE_CONFIG_FIELDSETS = WAVES_CONSTANCE_CONFIG_FIELDSETS


class WConstanceAppConfig(AppConfig):

    verbose_name = 'WAVES constants'
    name = "constance"

    def __init__(self, app_name, app_module):
        AppConfig.__init__(self, app_name, app_module)
