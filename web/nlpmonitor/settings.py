"""
Django settings for nlpmonitor project.

Generated by 'django-admin startproject' using Django 2.2.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'afnhvy-!a93^^v(^0&$+b*+5vu+*l1w5ki7z&f0-2pvet=89gg'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DJANGO_DEBUG', "True") == "True"

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'jet',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'stronghold',
    'django_extensions',
    'widget_tweaks',
    'rest_framework',
    'mainapp',
    'topicmodelling',
    'evaluation',
    'dashboard',
    'geo',
    'scraping',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'stronghold.middleware.LoginRequiredMiddleware',
]

STRONGHOLD_DEFAULTS = False

STRONGHOLD_PUBLIC_URLS = (
    r'/$',
    r'^/accounts/.+$',
    r'^/static/.+$',
)

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
}

ROOT_URLCONF = 'nlpmonitor.urls'

TEMPLATE_LATEX_DIR = os.path.join(BASE_DIR, 'templates_latex')
REPORT_IMAGE_DIR = os.path.join("/", 'report_images')

CUSTOM_CONTEXT_PROCESSORS = [
    'mainapp.context_processors.dashboard_list.dashboard_list',
]
if DEBUG:
    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [os.path.join(BASE_DIR, 'templates'), TEMPLATE_LATEX_DIR],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                ] + CUSTOM_CONTEXT_PROCESSORS,
            },
        },
    ]
else:
    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [os.path.join(BASE_DIR, 'templates'), TEMPLATE_LATEX_DIR],
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                    'django.template.context_processors.i18n',
                ] + CUSTOM_CONTEXT_PROCESSORS,
                'loaders': [
                    ('django.template.loaders.cached.Loader', [
                        'django.template.loaders.filesystem.Loader',
                        'django.template.loaders.app_directories.Loader',
                    ])
                ]
            },
        },
    ]

if DEBUG:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://redis:6379/0",
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "MAX_ENTRIES": 10000,
                "CULL_FREQUENCY": 10
            },
            "KEY_PREFIX": "nlpmonitor",
            "TIMEOUT": 60 * 60,
        }
    }

WSGI_APPLICATION = 'nlpmonitor.wsgi.application'


LOGIN_REDIRECT_URL = "/login_redirect/"

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('DB_NAME', 'nlpmonitor'),
        'USER': os.getenv('DB_USER', 'nlpmonitor'),
        'PASSWORD': os.getenv('DB_PASSWORD', '32193219'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', 5432),
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

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Asia/Almaty'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static_root')
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'staticfiles'),
)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media_root')

ES_INDEX_DOCUMENT = 'main_sharded'
ES_INDEX_EMBEDDING = 'embedding'

ES_INDEX_TOPIC_MODELLING = 'topic_modelling'
ES_INDEX_TOPIC_DOCUMENT = 'topic_document_sharded'  # f"{ES_INDEX_TOPIC_DOCUMENT}_{tm}"
ES_INDEX_TOPIC_COMBOS = 'topic_combos'  # f"{ES_INDEX_TOPIC_COMBOS}_{tm}"
ES_INDEX_TOPIC_DOCUMENT_UNIQUE_IDS = 'unique_ids_topic_document_sharded'  # f"{ES_INDEX_TOPIC_DOCUMENT_UNIQUE_IDS}_{tm}"
ES_INDEX_META_DTM = 'meta_dtm'
ES_INDEX_MAPPINGS = 'mappings'
ES_INDEX_DYNAMIC_TOPIC_MODELLING = 'dynamic_topic_modelling'
ES_INDEX_DYNAMIC_TOPIC_DOCUMENT = 'dynamic_topic_document'
ES_INDEX_DYNAMIC_TOPIC_DOCUMENT_UNIQUE_IDS = 'dynamic_topic_document_unique_ids'

ES_INDEX_DOCUMENT_EVAL = 'document_eval'  # f"{ES_INDEX_DOCUMENT_EVAL}_{tm}_{criterion.id}{_neg}"
ES_INDEX_DOCUMENT_EVAL_UNIQUE_IDS = 'unique_ids_document_eval'  # f"{ES_INDEX_DOCUMENT_EVAL_UNIQUE_IDS}_{tm}"

ES_INDEX_DICTIONARY_INDEX = 'dictionary_index'
ES_INDEX_DICTIONARY_WORD = 'dictionary_word'   # f"{ES_INDEX_DICTIONARY_WORD}_{name}{_temp}"
ES_INDEX_CUSTOM_DICTIONARY_WORD = 'custom_dictionary_word'

ES_INDEX_DOCUMENT_LOCATION = 'document_location'  # f"{ES_INDEX_DOCUMENT_EVAL}_{tm}_{criterion.id}"

ES_INDEX_SOURCE_CLUSTERS = 'cluster_source'

ES_INDEX_EVAL_DICT = 'eval_dict'

from elasticsearch import Elasticsearch
http_auth = None
es_username = os.getenv('DJANGO_ES_BASIC_AUTH_USERNAME', '')
es_password = os.getenv('DJANGO_ES_BASIC_AUTH_PASSWORD', '')
if es_username and es_password:
    http_auth = f"{es_username}:{es_password}"
if not DEBUG:
    hosts = [
        {
            'host': os.getenv('ES_HOST1', 'elasticsearch1'),
            'port': os.getenv('ES_PORT1', 9200),
            'http_auth': http_auth,
        },
        {
            'host': os.getenv('ES_HOST2', 'elasticsearch2'),
            'port': os.getenv('ES_PORT2', 9200),
            'http_auth': http_auth,
        },
        {
            'host': os.getenv('ES_HOST3', 'elasticsearch3'),
            'port': os.getenv('ES_PORT3', 9200),
            'http_auth': http_auth,
        },
    ]
else:
    hosts = [
        {
            'host': os.getenv('ES_HOST', 'elasticsearch1'),
            'port': os.getenv('ES_PORT1', 9200),
        },
    ]

ES_CLIENT = Elasticsearch(
    hosts=hosts,
    timeout=60,
    max_retries=10,
    retry_on_timeout=True,)

if not DEBUG:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=os.getenv('SENTRY_DSN_DJANGO'),
        integrations=[DjangoIntegration()]
    )

MIN_DOCS_PER_TAG = 1000
MIN_DOCS_PER_AUTHOR = 100

SHELL_PLUS_PRE_IMPORTS = (
    ('nlpmonitor.settings', ('ES_CLIENT', 'ES_INDEX_DOCUMENT', 'ES_INDEX_EMBEDDING',
                             'ES_INDEX_TOPIC_MODELLING', 'ES_INDEX_TOPIC_DOCUMENT',
                             'ES_INDEX_DICTIONARY_INDEX', 'ES_INDEX_DICTIONARY_WORD', 'ES_INDEX_DOCUMENT_EVAL',
                             'ES_INDEX_CUSTOM_DICTIONARY_WORD', 'ES_INDEX_DOCUMENT_EVAL_UNIQUE_IDS',
                             'ES_INDEX_TOPIC_DOCUMENT_UNIQUE_IDS', )),
    ('elasticsearch_dsl', ('Search', 'Index', 'Q')),
    'datetime',
)

EMAIL_HOST = os.getenv('DJANGO_EMAIL_HOST', '')
EMAIL_PORT = os.getenv('DJANGO_EMAIL_PORT', '')
EMAIL_HOST_USER = os.getenv('DJANGO_EMAIL_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('DJANGO_EMAIL_PASSWORD', '')
EMAIL_USE_SSL = True
DEFAULT_FROM_EMAIL = os.getenv('DJANGO_EMAIL_FROM', '')
