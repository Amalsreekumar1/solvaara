"""
Django settings for config project.

For the full list of settings and their values, see
https://docs.djangoproject.com/en/6.1/ref/settings/
"""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]

DEBUG = os.environ.get("DJANGO_DEBUG", "False") == "True"

ALLOWED_HOSTS = [h for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",") if h]
CSRF_TRUSTED_ORIGINS = [
    o for o in os.environ.get("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",") if o
]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'catalogue',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'catalogue.middleware.IndexingControlMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'catalogue.context_processors.categories',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database (SQLite: PythonAnywhere free accounts have no Postgres)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# Internationalization

LANGUAGE_CODE = "en-in"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True


# Static and media files
# In production, the host serves /static/ and /media/ directly.

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# Email (nothing is sent yet; enquiries are stored in the database)

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


# Business details (read from .env, never hardcoded in templates)

WHATSAPP_NUMBER = os.environ.get("DJANGO_WHATSAPP_NUMBER", "")
CONTACT_EMAIL = os.environ.get("DJANGO_CONTACT_EMAIL", "")
CONTACT_PHONE = os.environ.get("DJANGO_CONTACT_PHONE", "")
CONTACT_ADDRESS = os.environ.get("DJANGO_CONTACT_ADDRESS", "")
OPENING_HOURS = os.environ.get("DJANGO_OPENING_HOURS", "")
INSTAGRAM_URL = os.environ.get("DJANGO_INSTAGRAM_URL", "")
FACEBOOK_URL = os.environ.get("DJANGO_FACEBOOK_URL", "")
YOUTUBE_URL = os.environ.get("DJANGO_YOUTUBE_URL", "")


# Site address and search-engine indexing (off unless explicitly enabled)

SITE_URL = os.environ.get("DJANGO_SITE_URL", "").rstrip("/")
ALLOW_INDEXING = os.environ.get("DJANGO_ALLOW_INDEXING", "False") == "True"


# Production security

if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True