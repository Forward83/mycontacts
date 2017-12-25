"""
Django settings for contact project.

Generated by 'django-admin startproject' using Django 1.11.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
import dj_database_url
from django.conf.global_settings import MEDIA_ROOT, MEDIA_URL
from import_export.formats import base_formats
from decouple import config, Csv
import zipfile, tarfile

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = True
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())
# ALLOWED_HOSTS = ['.appspot.com', 'proven-center-186811.appspot.com',]

# Application definition

INSTALLED_APPS = [
    'contacts',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'import_export',
    'rest_framework',
    'storages',
]

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

REST_FRAMEWORK = {
    
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'contact.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'contact.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL')
    )
    #    'default': {
    #     'ENGINE': 'django.db.backends.mysql',
    #     'NAME': 'contacts',
    #     'USER': 'mycontact',
    #     'PASSWORD': 'P@ssw0rd123',
    #     'HOST': '35.198.128.5',   # Or an IP Address that your DB is hosted on
    #     'PORT': '3306',
    # }
}

DATABASES['default']['HOST'] = '/cloudsql/proven-center-186811:europe-west3:mycontact'
# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = False
if not os.getenv('GAE_INSTANCE'):
    DATABASES['default']['HOST'] = '127.0.0.1'
    DEBUG = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO'
        },
    },
}

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Kiev'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# static files (CSS, JavaScript, Images)
GS_BUCKET_NAME = '186811' # the name of the bucket you have created from the google cloud storage console
GS_PROJECT_ID = 'proven-center-186811'

DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
# STATICFILES_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'

# STATICFILES_DIRS = [
#     os.path.join(BASE_DIR, "static"),
#     ]

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/login'
MEDIA_ROOT = os.path.join(BASE_DIR, 'contacts/media')
MEDIA_URL = '/media/'
#Size for creating thumbnail
THUMB_SIZE = (125, 125)
#Maximum allowed photo size
PHOTO_SIZE = 2*1024*1024
#Default formats for import-export actions
DEFAULT_FORMATS_FOR_EXPORT = (base_formats.CSV, base_formats.XLS, base_formats.XLSX, base_formats.HTML)
DEFAULT_FORMATS_FOR_IMPORT = (base_formats.CSV, base_formats.XLS, base_formats.XLSX)
ARCHIVE_FORMAT_FOR_IMPORT = (('zip',), ('tar',), ('tar.gz',),)
MAX_SIZE_PHOTO_ARCHIVE = 7340032
