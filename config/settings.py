"""
Django settings for config project.
"""

import os
from pathlib import Path

import dj_database_url
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / '.env')

# Vercel'de calisirken SECRET_KEY zorunlu: eksikse sessizce bilinen gelistirme
# anahtarina dusmek yerine acilista hata verir.
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    if os.environ.get('VERCEL'):
        raise ImproperlyConfigured('SECRET_KEY ortam degiskeni tanimli olmali.')
    SECRET_KEY = 'django-insecure-dev-key-change-me'

# Varsayilan kapali; lokalde .env'deki DEBUG=True ile acilir.
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
    if host.strip()
]

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get('CSRF_TRUSTED_ORIGINS', 'http://localhost:8000').split(',')
    if origin.strip()
]

# Vercel her deployment'a (production ve her preview'a) kendi domainini
# VERCEL_URL olarak otomatik veriyor; bu deploy'dan once bilinmedigi icin
# ALLOWED_HOSTS/CSRF_TRUSTED_ORIGINS'e elle eklenemez, burada otomatik eklenir.
VERCEL_URL = os.environ.get('VERCEL_URL')
if VERCEL_URL:
    ALLOWED_HOSTS.append(VERCEL_URL)
    CSRF_TRUSTED_ORIGINS.append(f'https://{VERCEL_URL}')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'accounts',
    'lessons',
    'quizzes',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
#
# DATABASE_URL tanimli degilse (lokal gelistirme) SQLite'a dusulur.
# Uretimde Supabase transaction pooler (port 6543) kullanilir.
#
# 'manage.py test' her zaman SQLite kullanir: Supabase'in pooler'i test
# veritabanini yaratip silme dongusunu yavaslatiyor ve DROP DATABASE'i
# tikayabiliyor. Diger tum komutlar (runserver, migrate, load_content, ...)
# .env'deki DATABASE_URL'i kullanmaya devam eder.
import sys

RUNNING_TESTS = 'test' in sys.argv

DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL and not RUNNING_TESTS:
    DATABASES = {
        'default': dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=0,
            ssl_require=True,
        )
    }
    DATABASES['default']['DISABLE_SERVER_SIDE_CURSORS'] = True
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'tr'

TIME_ZONE = 'Europe/Istanbul'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Manifest'li (hash'li dosya adi) storage collectstatic gerektirir; lokalde ve
# testlerde (Django test runner settings.DEBUG'i gecici olarak False yapar,
# ManifestStaticFilesStorage bu yuzden .env'deki DEBUG yerine buradaki DEBUG
# degiskenine gore seciliyor) collectstatic calismadigi icin manifestsiz storage kullanilir.
STORAGES = {
    'staticfiles': {
        'BACKEND': (
            'whitenoise.storage.CompressedStaticFilesStorage' if DEBUG
            else 'whitenoise.storage.CompressedManifestStaticFilesStorage'
        ),
    },
}

# Build sirasinda collectstatic calisamazsa yedek cozum:
WHITENOISE_USE_FINDERS = DEBUG

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'


# Guvenlik (sadece DEBUG=False: lokal runserver http uzerinde calismaya devam eder).
# SECURE_SSL_REDIRECT bilerek acik degil: Vercel zaten HTTPS'e yonlendiriyor,
# proxy arkasinda ikinci bir yonlendirme dongu riski tasir.
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_HSTS_SECONDS = 3600
