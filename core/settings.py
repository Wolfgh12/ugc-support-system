import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-ugc-project-key-2026'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# --- CRITICAL FIX FOR FETCH REQUESTS ---
APPEND_SLASH = True
CSRF_TRUSTED_ORIGINS = ['http://127.0.0.1:8000', 'http://localhost:8000']

# Application definition
# NOTICE: 'tickets' is placed ABOVE 'django.contrib.admin' to allow template overriding
INSTALLED_APPS = [
    'tickets', 
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
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

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Ensures BASE_DIR/templates is checked first
        'DIRS': [BASE_DIR / 'templates'], 
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

WSGI_APPLICATION = 'core.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# --- STATIC FILES CONFIGURATION ---
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# --- EMAIL NOTIFICATION CONFIGURATION ---
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# Your Verified Gmail
EMAIL_HOST_USER = 'nanayeezy@gmail.com' 
EMAIL_HOST_PASSWORD = 'skctccwpxkuqqzpj' 
DEFAULT_FROM_EMAIL = f"UGC Support <{EMAIL_HOST_USER}>"

# --- UNIVERSITY NOTIFICATION SETTINGS ---
UNIVERSITY_CENTRAL_EMAIL = 'university-enquiries@ugc.edu.gh'

UGC_DEPARTMENTS = {
    'I.T.': 'it-support@ugc.edu.gh',
    'Admission': 'admissions@ugc.edu.gh', 
    'Finance': 'finance@ugc.edu.gh',
    'HR': 'hr@ugc.edu.gh',
    'Student Support': 'support@ugc.edu.gh',
}

# --- SECURITY & TIMEOUT ---
EMAIL_TIMEOUT = 10 

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'