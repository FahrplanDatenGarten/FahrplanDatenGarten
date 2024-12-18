"""
Django settings for fahrplandatengarten project.

Generated by 'django-admin startproject' using Django 2.2.6.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import configparser
import os
import logging

config = configparser.RawConfigParser()
try:
    if 'FDG_CONFIG_FILE' in os.environ:
        # Use read to avoid failing when file is not existing. This allows for auto creation in the given directory
        config.read(os.environ.get('FDG_CONFIG_FILE', ''), encoding='utf-8')
    else:
        config.read(['fdg.cfg', '/etc/fdg/fdg.cfg'], encoding='utf-8')
except configparser.Error as e:
    logging.critical((
        '{0} occured while parsing the configuration at {1}:{2}:\n'
        '{3}\nNote: {4}'
    ).format(
        type(e).__name__,
        e.source,
        e.lineno,
        e,
        type(e).__doc__.splitlines()[0]
    ))
    exit(1)

if not len(config.sections()):
    logging.critical("No configuration file could be found!")
    exit(1)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config.get("general", "secret_key")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config.getboolean('general', 'debug', fallback=True)

ALLOWED_HOSTS = config.get("general", 'allowed_hosts', fallback="*").split(',')

INTERNAL_IPS = [
    '127.0.0.1',
    '::1'
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bootstrap4',
    'fahrplandatengarten.core',
    'fahrplandatengarten.DBApis',
    'fahrplandatengarten.FGRFiller',
    'fahrplandatengarten.verspaeti',
    'fahrplandatengarten.gtfs',
    'fahrplandatengarten.netzkarte',
    'fahrplandatengarten.details',
    'fahrplandatengarten.wagenreihung',
    'debug_toolbar'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF = 'fahrplandatengarten.fahrplandatengarten.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'fahrplandatengarten.fahrplandatengarten.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

db_backend = config.get('database', 'engine', fallback='sqlite3')
if db_backend == 'postgresql_psycopg2':
    db_backend = 'postgresql'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.' + db_backend,
        'NAME': config.get('database', 'name', fallback='db.sqlite3'),
        'USER': config.get('database', 'user', fallback=''),
        'PASSWORD': config.get('database', 'password', fallback=''),
        'HOST': config.get('database', 'host', fallback=''),
        'PORT': config.get('database', 'port', fallback=''),
        'CONN_MAX_AGE': 0 if db_backend == 'sqlite3' else 120
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'de-de'

TIME_ZONE = config.get("general", "time_zone", fallback='Europe/Berlin')

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]
STATIC_ROOT = config.get("general", "static_root", fallback=None)

# Added SCSS to Compress
COMPRESS_PRECOMPILERS = [
    ('text/x-scss', 'django_libsass.SassCompiler'),
]
LIBSASS_SOURCE_COMMENTS = False
COMPRESS_ROOT = os.path.join(BASE_DIR, "static")

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

if config.has_option('caching', 'redis_location'):
    CACHES['redis'] = {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": config.get('caching', 'redis_location'),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
    CACHES['default'] = CACHES['redis']

# Celery configuration
# https://docs.celeryproject.org/en/latest/userguide/configuration.html

CELERYCONF_RESULT_BACKEND = config.get(
    'celery',
    'result_backend',
    fallback='redis://localhost/0')

CELERYCONF_BROKER_URL = config.get(
    'celery',
    'broker_url',
    fallback='redis://localhost/0')

CELERYCONF_TASK_SERIALIZER = 'json'

CELERYCONF_TASK_IGNORE_RESULT = config.getboolean(
    'celery', 'task_ignore_result', fallback=False)

CELERYCONF_TASK_STORE_ERRORS_EVEN_IF_IGNORED = config.getboolean(
    'celery', 'task_store_errors_even_if_ignored', fallback=True)

# fahrplandatengarten's custom configuration
PERIODIC_IMPORT_TIMETABLES = config.get(
    "periodic", 'timetables', fallback="*,*/15").split(',')

PERIODIC_IMPORT_JOURNEYS = config.get(
    "periodic", 'journeys', fallback="*,*/5").split(',')

PERIODIC_IMPORT_WAGENREIHUNGEN = config.get(
    "periodic", 'wagenreihungen', fallback="*,*/15").split(',')

RIS_APIS = {section.split('.')[1]: {
    "url": config.get(section, "url"),
    "client_id": config.get(section, "client_id"),
    "api_key": config.get(section, "api_key"),
} for section in filter(lambda name: name.startswith("ris."), config.sections())}
