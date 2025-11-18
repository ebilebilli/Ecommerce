import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load env
load_dotenv(dotenv_path=BASE_DIR / '.env.docker')

# Security
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-change-this')
DEBUG = os.environ.get('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = ['*']

# CSRF
CSRF_TRUSTED_ORIGINS = ['http://127.0.0.1:8001', 'http://localhost:8001']

# config/settings.py - ƏLAVƏ EDİN
PRODUCT_SERVICE_URL = os.environ.get('PRODUCT_SERVICE_URL', 'http://product-service:8000')

# Installed apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'analitic',
    'drf_yasg',
    'drf_spectacular',
]



MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # static fayllar üçün
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

REST_FRAMEWORK = {
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.URLPathVersioning',
    'DEFAULT_VERSION': 'v1',
    'ALLOWED_VERSIONS': ('v1', 'v2'),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}



SPECTACULAR_SETTINGS = {
    'TITLE': 'Analitic API',
    'DESCRIPTION': 'Analitic servisin API endpoint-ləri',
    'VERSION': 'v1',
    'CONTACT': {'email': 'ilham@example.com'},
    'LICENSE': {'name': 'BSD License'},
}






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

WSGI_APPLICATION = 'config.wsgi.application'

# Local Windows üçün:
if os.environ.get("DOCKER", None) == "1":
    DB_HOST = os.environ.get("POSTGRES_HOST", "db-analytic")  # Docker Compose konteyner adı

else:
    DB_HOST = os.environ.get("POSTGRES_HOST", "127.0.0.1")  # Lokal host

# config/settings.py - DÜZƏLDİN
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'analytic_db'),         # ✅ DÜZGÜN
        'USER': os.environ.get('DB_USER', 'analytic_user'),       # ✅ DÜZGÜN
        'PASSWORD': os.environ.get('DB_PASSWORD', '12345'),       # ✅ DÜZGÜN
        'HOST': DB_HOST,
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
