"""
Django settings for H5Mess project.

Generated by 'django-admin startproject' using Django 4.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.as_posix()
MEDIA_ROOT = BASE_DIR + '/media'
MEDIA_URL = "/media/"

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-fe1navnc)ec$1-6d*)x8q4o#ihzfu@y79mkz($1ut!xrtfub_f"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]
DATE_INPUT_FORMATS = ['%d-%m-%Y']
CSRF_TRUSTED_ORIGINS = [
    "https://54e1-2405-204-20a6-ba3a-144f-777b-6d7b-5032.in.ngrok.io", "http://127.0.0.1:8000/admin/", "https://05b1-117-212-15-22.in.ngrok.io/"]

WEIGHT_MACHINES = 1

# Application definition


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "mess",
    "rest_framework",
    "django_cleanup.apps.CleanupConfig"
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "H5Mess.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "H5Mess.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR + "/db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Kolkata"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/
STATIC_ROOT = BASE_DIR + '/static'
STATIC_URL = "/static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
# SSO APP KEYS
CLIENT_ID = "YDcbZXL05PnPgvRVf7MvrzYCE13mYlUhz8ABIFP6"
CLIENT_SECRET = "VgrxOyFsKGYQ93x8a4tu1bOc7gxzkEhfbXU4YgRWkrym3GmS7br9ZzzBfqlGfDkDYnXoxLQqqV1qhgdJHOgeMhk63xx2epn4EM71kG8TyMX1d3qMtIipSeogYj6LD1Rw"
REDIRECT_URI = "https://gymkhana.iitb.ac.in/~hostel5/"

# SSO API URlS
TOKEN_EXCHANGE_URL = "https://gymkhana.iitb.ac.in/profiles/oauth/token/"
RESOURCES_URL = "https://gymkhana.iitb.ac.in/profiles/user/api/user/?fields=id,first_name,last_name,username,roll_number"
