from __future__ import unicode_literals
import environ
import sys
from os.path import dirname, join, exists


BASE_DIR = dirname(dirname(dirname(__file__)))
STATIC_URL = '/static/'

MEDIA_ROOT = join(BASE_DIR, 'media')

MEDIA_URL = "/media/"

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            join(BASE_DIR, 'waves', 'templates'),
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
                # 'waves.utils.context_theme_processor.css_theme',
            ],
        },
    },
]

# Django main environment file (issued from local.env)
env = environ.Env()
# Ideally move env file should be outside the git repo
# i.e. BASE_DIR.parent.parent
env_file = join(dirname(__file__), 'local.env')
if exists(env_file):
    environ.Env.read_env(str(env_file))
# SECURITY WARNING: keep the secret key used in production secret!
# Raises ImproperlyConfigured exception if SECRET_KEY not in os.environ
SECRET_KEY = env.str('SECRET_KEY')
# DATABASE configuration
DATABASES = {
    'default': env.db(default='sqlite:///' + BASE_DIR + '/waves/db/waves.sample.sqlite3'),
}

if 'test' in sys.argv:
    DATABASES['default']['ENGINE'] = 'django.db.backends.sqlite3'

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')
REGISTRATION_SALT = env.str('REGISTRATION_SALT')
# Django countries configuration
COUNTRIES_FIRST = env.list('COUNTRIES_FIRST', default=['FR','GB','US','DE'])
# DJANGO DEBUG global
DEBUG = env.bool('DEBUG', default=False)
# LOG FILE ROOT
LOG_ROOT = env.str('LOG_ROOT', default=dirname(BASE_DIR) + '/logs')
WAVES_ENV_FILE = env.str('WAVES_ENV_FILE', default=join(BASE_DIR, 'waves', 'config', 'waves.env'))
STATIC_ROOT = env.str('STATIC_ROOT', default=join(dirname(BASE_DIR), 'staticfiles'))
ROOT_LOG_LEVEL = env.str('ROOT_LOG_LEVEL', default='ERROR')
WAVES_LOG_LEVEL = env.str('WAVES_LOG_LEVEL', default=ROOT_LOG_LEVEL)
CRON_LOG_LEVEL = env.str('CRON_LOG_LEVEL', default=ROOT_LOG_LEVEL)
SAGA_LOG_LEVEL = env.str('SAGA_LOG_LEVEL', default=ROOT_LOG_LEVEL)

# Application definition
INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'authtools',
    'grappelli',
    'django.contrib.admin',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'jquery_ui',
    'tabbed_admin',
    # WAVES required dependencies
    # 'django-log-file-viewer',
    'polymorphic',
    'smart_selects',
    'mptt',
    'eav',
    'nested_admin',
    'django_crontab',
    'django_countries',
    'crispy_forms',
    'easy_thumbnails',
    'mail_templated',
    'rest_framework',
    'waves.apps.WavesApp',
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

WSGI_APPLICATION = 'waves_services.wsgi.application'

LANGUAGE_CODE = 'en-gb'

TIME_ZONE = 'Europe/Paris'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Authentication Settings
AUTH_USER_MODEL = 'authtools.User'

# Thumbnails configuration
THUMBNAIL_EXTENSION = 'png'  # Or any extn for your thumbnails
THUMBNAIL_MEDIA_ROOT = '/home/marc'

# DRF Configuration
REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
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
# FILE_UPLOAD_MAX_MEMORY_SIZE = 0FILE_UPLOAD_DIRECTORY_PERMISSIONS
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755
FILE_UPLOAD_PERMISSIONS = 0o775

# Default Site id
SITE_ID = 1

# Tabbed Admin configuration
TABBED_ADMIN_USE_JQUERY_UI = False
THUMBNAIL_EXTENSION = 'png'
