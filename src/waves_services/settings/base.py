from __future__ import unicode_literals
import environ
from os.path import dirname, join, exists
from django.core.urlresolvers import reverse_lazy

env = environ.Env()
root = environ.Path(__file__) - 4

ROOT_DIR = str(root.path())
BASE_DIR = str(root.path('src'))
MEDIA_ROOT = str(root.path('media'))
MEDIA_URL = '/media/'
# Use Django templates using the new Django 1.8 TEMPLATES settings
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            join(BASE_DIR, 'templates'),
            # insert more TEMPLATE_DIRS here
            # join(BASE_DIR, 'waves', 'templates'),
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
                'waves.utils.context_theme_processor.css_theme',
            ],
        },
    },
]

# SECURITY WARNING: keep the secret key used in production secret!
# Raises ImproperlyConfigured exception if SECRET_KEY not in os.environ
SECRET_KEY = env.str('SECRET_KEY', "You-should-consider-setting-a-secret-key")

# Application definition
INSTALLED_APPS = (
    'polymorphic',
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'authtools',
    'tabbed_admin',
    'grappelli',
    'django.contrib.admin',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    # WAVES required dependencies
    # 'django-log-file-viewer',
    'mptt',
    'eav',
    'nested_admin',
    'django_crontab',
    'django_countries',
    'crispy_forms',
    'easy_thumbnails',
    'mail_templated',
    'waves.apps.WavesApp',
    'rest_framework',
    'corsheaders',
    'rest_framework_docs',
    # WAVES optional dependencies
    'ckeditor',
    'bootstrap_themes',
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

ROOT_URLCONF = 'waves_services.urls'

# DATABASE configuration
DATABASES = {
    'default': env.db(default='sqlite:///' + ROOT_DIR + '/db/waves.sample.sqlite3'),
}

WSGI_APPLICATION = 'waves_services.wsgi.application'

LANGUAGE_CODE = 'en-gb'

TIME_ZONE = 'Europe/Paris'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATICFILES_DIRS = [
    join(BASE_DIR, 'static'),
    # join(BASE_DIR, 'waves', 'static')
]
STATIC_URL = '/static/'
STATIC_ROOT = join(dirname(BASE_DIR), 'staticfiles')

################################################
#    --------- WAVES CONFIGURATION ---------   #
################################################
# Bootstrap theme default
# BOOTSTRAP_THEME = 'darkly'

# Crispy Configuration
CRISPY_TEMPLATE_PACK = 'trucmuche'
# WAVES_ENV_FILE = 'waves333.env'
# Authentication Settings
AUTH_USER_MODEL = 'authtools.User'

# Thumbnails configuration
THUMBNAIL_EXTENSION = 'png'  # Or any extn for your thumbnails
THUMBNAIL_MEDIA_ROOT = MEDIA_ROOT

# Two step registration configuration

# GRAPPELLI configuration
# GRAPPELLI_ADMIN_TITLE = 'WAVES Services Administration'

# Django countries configuration
COUNTRIES_FIRST = [
    'FR',
    'GB',
    'US',
    'DE'
]

# DRF Configuration
REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        # 'waves.api.authentication.auth.WavesAPI_KeyAuthBackend',
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.BasicAuthentication',
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

# File Upload configuration
FILE_UPLOAD_HANDLERS = [
    "django.core.files.uploadhandler.TemporaryFileUploadHandler"
]
FILE_UPLOAD_MAX_MEMORY_SIZE = 0

# Default Site id
SITE_ID = 1
# TODO add recaptcha for registration

# Tabbed Admin configuration
TABBED_ADMIN_USE_JQUERY_UI = False
# DEBUG
DEBUG = env.bool('DEBUG', default=False)
THUMBNAIL_DEBUG = DEBUG
TEMPLATES[0]['OPTIONS'].update({'debug': DEBUG})
# LOG FILE ROOT
WAVES_LOG_ROOT = env.str('WAVES_LOG_ROOT', default=ROOT_DIR + '/logs')

if DEBUG:
    print "loaded settings from base"