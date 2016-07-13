"""
Django settings for waves project.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""
from __future__ import unicode_literals

from django.core.urlresolvers import reverse_lazy
from os.path import dirname, join, exists
from django.contrib import messages
import environ
# Build paths inside the project like this: join(BASE_DIR, "directory")
if 'env' not in vars():
    env = environ.Env()
    ENV = environ.Env()
    root = environ.Path(__file__) - 4
    # Ideally move env file should be outside the git repo
    # i.e. BASE_DIR.parent.parent
    ENV_FILE = join(dirname(__file__), 'waves.env')
    if exists(ENV_FILE):
        environ.Env.read_env(str(ENV_FILE))
    else:
        raise RuntimeError('Unable to process WAVES environment data')

BASE_DIR = str(root.path('src'))
MEDIA_ROOT = env.str('MEDIA_ROOT', str(root.path('media')))
MEDIA_URL = env.str('MEDIA_URL', "/media/")
# Use Django templates using the new Django 1.8 TEMPLATES settings
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            join(BASE_DIR, 'templates'),
            # insert more TEMPLATE_DIRS here
            join(BASE_DIR, 'waves', 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
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

# SECURITY WARNING: keep the secret key used in production secret!
# Raises ImproperlyConfigured exception if SECRET_KEY not in os.environ
SECRET_KEY = env.str('SECRET_KEY')

# Application definition
INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'authtools',
    'grappelli',
    'tabbed_admin',
    'django.contrib.admin',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    # WAVES dependencies
    'mptt',
    'eav',
    'nested_admin',
    'django_crontab',
    'django_countries',
    'crispy_forms',
    'easy_thumbnails',
    # WAVES APPS
    'waves',
    'waves.api',
    'waves.accounts',
    'waves.profiles',
    # WAVES API dependencies
    'rest_framework',
    'corsheaders',
    'rest_framework_docs',
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

DATABASES = {
    'default': env.db(),
}

WSGI_APPLICATION = 'waves_services.wsgi.application'

LANGUAGE_CODE = 'en-gb'

TIME_ZONE = 'Europe/Paris'

USE_I18N = True

USE_L10N = True

USE_TZ = env.bool('USE_TZ')

STATICFILES_DIRS = [
    join(BASE_DIR, 'static'),
    join(BASE_DIR, 'waves', 'static')
]
STATIC_URL = '/static/'
STATIC_ROOT = join(dirname(BASE_DIR), 'staticfiles')

# Crispy Form Theme - Bootstrap 3
CRISPY_TEMPLATE_PACK = 'bootstrap3'

MESSAGE_TAGS = {
    messages.SUCCESS: 'success success',
    messages.WARNING: 'warning warning',
    messages.ERROR: 'danger error'
}

# Authentication Settings
AUTH_USER_MODEL = 'authtools.User'
LOGIN_REDIRECT_URL = reverse_lazy("profiles:show_self")
LOGIN_URL = reverse_lazy("accounts:login")

THUMBNAIL_EXTENSION = 'png'  # Or any extn for your thumbnails
THUMBNAIL_MEDIA_ROOT = MEDIA_ROOT

ACCOUNT_ACTIVATION_DAYS = 7
REGISTRATION_SALT = 'waves-registration-salt'
REGISTRATION_ALLOWED = True

GRAPPELLI_ADMIN_TITLE = 'WAVES Services Administration'

COUNTRIES_FIRST = [
    'FR',
    'GB',
    'US'
]

# Site admin
SITE_ID = 1
JET_SIDE_MENU_COMPACT = True
# DRF Configuration
REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'waves.api.authentication.auth.WavesAPI_KeyAuthBackend',
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
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

# FileUploads
FILE_UPLOAD_HANDLERS = [
    "django.core.files.uploadhandler.TemporaryFileUploadHandler"
]

FILE_UPLOAD_MAX_MEMORY_SIZE = 0

TEST_RUNNER = 'waves.tests.runner.WavesTestRunner'
# RE-CAPTCHA
RECAPTCHA_PUBLIC_KEY = '6LdLZx0TAAAAAIzYJQMcB5YPcWAg2fBKy5NI3QmK'
RECAPTCHA_PRIVATE_KEY = '6LdLZx0TAAAAADyqVdsZrkJleprRg-sW18yJsL3g'
TABBED_ADMIN_USE_JQUERY_UI = False
