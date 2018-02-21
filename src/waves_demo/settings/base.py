"""
Main WAVES application settings files
"""
from __future__ import unicode_literals

from os.path import dirname, join, isfile

LOGGING_CONFIG = None
BASE_DIR = dirname(dirname(dirname(dirname(__file__))))
SRC_DIR = join(BASE_DIR, 'src')
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            join(SRC_DIR, 'templates'),
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
    'django.contrib.staticfiles',
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'authtools',
    'jet',
    'jet.dashboard',
    'polymorphic',
    'django.contrib.sites',
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
    'corsheaders',
    'rest_framework',
    'rest_framework.authtoken'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'request_logging.middleware.LoggingMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"

# URLS
ROOT_URLCONF = 'waves_demo.urls'
WSGI_APPLICATION = 'waves_demo.wsgi.application'

# LANGUAGE CONFIGURATON
LANGUAGE_CODE = 'en-gb'
TIME_ZONE = 'Europe/Paris'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# SITE CONFIGURATION
SITE_ID = 1

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

# STATICS & MEDIA
STATIC_URL = '/static/'
MEDIA_ROOT = join(BASE_DIR, 'src', 'media')
MEDIA_URL = "/media/"
STATIC_ROOT = join(BASE_DIR, 'staticfiles')
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# CKEDITOR CONFIGURATION
CKEDITOR_CONFIGS = {
    'default': {
        'height': 150,
    },
}

# DJANGO JET CONFIGURATION
JET_SIDE_MENU_COMPACT = True
JET_CHANGE_FORM_SIBLING_LINKS = False

# CRISPY CONFIGURATION
CRISPY_TEMPLATE_PACK = 'bootstrap3'

# WCORE SERVICE / SUBMISSION MODELS
WCORE_SERVICE_MODEL = 'demo.DemoWavesService'
WCORE_SUBMISSION_MODEL = 'demo.DemoWavesSubmission'
