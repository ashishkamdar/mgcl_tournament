import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-p#v$dze+s+0kgc*ar(up1!5m34^vx$p#_e4j0!6m0dt9n%o-$f'

# SECURITY WARNING: don't run with debug turned on in production!
# Set to False when actually going live to prevent leaking code errors.
DEBUG = False 

ALLOWED_HOSTS = ['mgcl.areakpi.in', '127.0.0.1', 'localhost']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tournament',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CSRF_TRUSTED_ORIGINS = ['https://mgcl.areakpi.in', 'https://mgdemo.areakpi.in']

ROOT_URLCONF = 'mgcl_tournament.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], # Added to allow template overrides for admin
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'mgcl_tournament.wsgi.application'

# Database - Pointing to your Master SQLite file
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db_mgcl_2026_master.sqlite3',
    }
}

# Fix for the W042 Warnings in your logs
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

STATICFILES_DIRS = [
    BASE_DIR / "team_icons",
    BASE_DIR / "event_logos",
]

# Static & Media Files Configuration
STATIC_URL = 'static/'
# This tells Django where to collect files for Nginx
STATIC_ROOT = BASE_DIR / 'static' 

MEDIA_URL = '/media/'
#MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata' # Updated for local club context
USE_I18N = True
USE_TZ = True

# Authentication Settings
# Updated to use the name 'login_selection' as defined in your urls.py
LOGIN_URL = 'login_selection'            
LOGIN_REDIRECT_URL = 'fixtures'
LOGOUT_REDIRECT_URL = 'login_selection'