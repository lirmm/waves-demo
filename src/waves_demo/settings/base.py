"""
Main WAVES application settings files
"""
from __future__ import unicode_literals

from os.path import dirname, join, isfile


LOGGING_CONFIG = None
BASE_DIR = dirname(dirname(dirname(dirname(__file__))))

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            join(BASE_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# LOG FILE ROOC
LOG_ROOT = BASE_DIR + '/logs'

# Application definition
INSTALLED_APPS = (
    'polymorphic_tree',
    'django.contrib.staticfiles',
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'authtools',
    'jet',
    'jet.dashboard',
    'polymorphic',
    'django.contrib.admin',
    'django.contrib.sessions',
    'django.contrib.messages',
    'mptt',
    'waves.wcore',
    'demo',
    # WAVES required dependencies
    'adminsortable2',
    'accounts',
    'ckeditor',
    'django_countries',
    'crispy_forms',
    'easy_thumbnails',
    'mail_templated',
    'profiles',
    'rest_framework',
    'rest_framework.authtoken'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

SESSION_ENGINE="django.contrib.sessions.backends.signed_cookies"

ROOT_URLCONF = 'waves_demo.urls'
WSGI_APPLICATION = 'waves_demo.wsgi.application'
LANGUAGE_CODE = 'en-gb'
TIME_ZONE = 'Europe/Paris'
USE_I18N = True
USE_L10N = True
USE_TZ = True
# Authentication Settings
AUTH_USER_MODEL = 'authtools.User'
# Thumbnails configuration
THUMBNAIL_EXTENSION = 'png'  # Or any extn for your thumbnails
# DRF Configuration
REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework_xml.parsers.XMLParser',
        'rest_framework.parsers.MultiPartParser',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
        'rest_framework_xml.renderers.XMLRenderer',
    ),
    'TEST_REQUEST_DEFAULT_FORMAT': 'json'
}
# FILE_UPLOAD_MAX_MEMORY_SIZE = 0FILE_UPLOAD_DIRECTORY_PERMISSIONS
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755
FILE_UPLOAD_PERMISSIONS = 0o775
# Django countries first items
COUNTRIES_FIRST = ['FR', 'GB', 'US', 'DE']

ACCOUNT_ACTIVATION_DAYS = 7 # One-week activation window; you may, of course, use a different value.


# STATICS
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    join(BASE_DIR, "static"),
]
MEDIA_ROOT = join(BASE_DIR, 'src', 'media')
MEDIA_URL = "/media/"
STATIC_ROOT = join(BASE_DIR, 'staticfiles')
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

JET_SIDE_MENU_COMPACT = True

CKEDITOR_CONFIGS = {
    'default': {
        'height': 150,
    },
}
# TODO in order to enable sibling, either overwrite to set-it up per model, or add custom filter for submissions
# (keep current service)
JET_CHANGE_FORM_SIBLING_LINKS = False

CRISPY_TEMPLATE_PACK = 'bootstrap3'

ACCOUNT_ACTIVATION_DAYS = 7

# WAVES
WAVES_CORE = {
    'ACCOUNT_ACTIVATION_DAYS': 14,
    'ADMIN_EMAIL': 'admin_waves@atgc-montpellier.fr',
    'ALLOW_JOB_SUBMISSION': True,
    'APP_NAME': 'WAVES DEMO',
    'SERVICES_EMAIL': 'services@atgc-montpellier.fr',
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
WCORE_SERVICE_MODEL = 'demo.DemoWavesService'
WCORE_SUBMISSION_MODEL = 'demo.DemoWavesSubmission'
# MAILS
DEFAULT_FROM_EMAIL = 'WAVES <waves-demo@atgc-montpellier.fr>'
