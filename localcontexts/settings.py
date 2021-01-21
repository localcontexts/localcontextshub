"""
Django settings for localcontexts project.

Generated by 'django-admin startproject' using Django 3.0.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['PROD_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ['DEBUG_VALUE']

ALLOWED_HOSTS = ['localhost','127.0.0.1', 'localcontexts.herokuapp.com']

# https://docs.djangoproject.com/en/3.1/ref/settings/#std:setting-ADMINS
# For when DEBUG = FALSE, sends emails with site errors
SITE_ADMIN_NAME = os.environ['SITE_ADMIN_NAME']
SITE_ADMIN_EMAIL = os.environ['SITE_ADMIN_EMAIL']
ADMINS = [(SITE_ADMIN_NAME, SITE_ADMIN_EMAIL)]


# Application definition
INSTALLED_APPS = [
    'accounts.apps.AccountsConfig',
    'notifications.apps.NotificationsConfig',
    'bclabels.apps.BclabelsConfig',

    'pages',
    'communities',
    'institutions',
    'researchers',
    'api',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django_countries',
    'phone_field',
    'django_cleanup',
    'storages',

    'rest_framework',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'localcontexts.urls'

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

WSGI_APPLICATION = 'localcontexts.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASS'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT')
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Messages
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.ERROR: 'error-msg',
    messages.SUCCESS: 'success-msg',
    messages.INFO: 'info-msg',
}

# Config for sending out emails
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = 587
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True

USE_S3 = os.environ.get('USE_S3') == 'TRUE'

if USE_S3:

    #S3 BUCKETS CONFIG
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')

    AWS_LOCATION = 'static'
    AWS_S3_CUSTOM_DOMAIN='%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
    AWS_S3_OBJECT_PARAMETERS = {    
        'CacheControl': 'max-age=86400',
    }
    STATIC_LOCATION = 'static'
    STATIC_URL='https://%s/%s/' % (AWS_S3_CUSTOM_DOMAIN, AWS_LOCATION)
    ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'
    STATICFILES_FINDERS = ( 
        'django.contrib.staticfiles.finders.FileSystemFinder',    
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    )

    #Make default ACL publicly readable
    AWS_DEFAULT_ACL = 'public-read'

    # django-storages config
    AWS_S3_FILE_OVERWRITE = False
    AWS_DEFAULT_ACL = None
    # DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    DEFAULT_FILE_STORAGE = 'localcontexts.storage_backends.MediaStorage'
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

    # s3 public media settings
    PUBLIC_MEDIA_LOCATION = 'media'
    # MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{PUBLIC_MEDIA_LOCATION}/'
    MEDIA_URL = 'https://{AWS_S3_CUSTOM_DOMAIN}/{PUBLIC_MEDIA_LOCATION}/'

    DEFAULT_FILE_STORAGE = 'hello_django.storage_backends.PublicMediaStorage'
else:
    # Static files (CSS, JavaScript, Images)
    # https://docs.djangoproject.com/en/3.0/howto/static-files/

    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    STATIC_URL = '/static/'

    # Media Folder Settings
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
    MEDIA_URL = '/media/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'localcontexts/static')
]

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10
}
