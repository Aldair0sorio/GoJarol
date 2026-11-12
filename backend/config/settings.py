"""
Configuración de Django para Go Jarol.
Los valores sensibles se leen del archivo .env (que nunca se sube a Git).
"""

import sys
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent

# Permite importar el módulo de ML (carpeta ml/ en la raíz del repo)
sys.path.append(str(BASE_DIR.parent))

env = environ.Env()
if (BASE_DIR / '.env').exists():
    environ.Env.read_env(BASE_DIR / '.env')
elif (BASE_DIR.parent / '.env').exists():
    environ.Env.read_env(BASE_DIR.parent / '.env')

# --- Seguridad y entorno (vienen del .env) ---
SECRET_KEY = env('SECRET_KEY')
DEBUG = env.bool('DEBUG', default=False)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['*'])
if not ALLOWED_HOSTS or ALLOWED_HOSTS == ['']:
    ALLOWED_HOSTS = ['*']
if '*' not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.extend(['gojarol.tecnodesarrollo.site', 'jarol.tecnodesarrollo.site', 'localhost', '127.0.0.1', 'backend', '*'])

CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[
    'https://gojarol.tecnodesarrollo.site',
    'https://jarol.tecnodesarrollo.site',
    'http://localhost:5173',
    'http://127.0.0.1:3000',
])
if 'https://gojarol.tecnodesarrollo.site' not in CSRF_TRUSTED_ORIGINS:
    CSRF_TRUSTED_ORIGINS.append('https://gojarol.tecnodesarrollo.site')

CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[
    'https://gojarol.tecnodesarrollo.site',
    'https://jarol.tecnodesarrollo.site',
    'http://localhost:5173',
    'http://127.0.0.1:3000',
])
CORS_ALLOW_ALL_ORIGINS = True


# --- Aplicaciones ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Librerías
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',

    # Nuestras apps
    'accounts',
    'curriculum',
    'exercises',
    'chat',
    'progress',
    'classes',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # debe ir arriba de CommonMiddleware
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
        'DIRS': [],
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


# --- Base de datos (PostgreSQL o SQLite según DATABASE_URL del .env) ---
DATABASES = {
    'default': env.db('DATABASE_URL', default='sqlite:///db.sqlite3')
}


# --- Usuario propio ---
AUTH_USER_MODEL = 'accounts.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# --- API REST ---
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}


# --- Idioma y zona horaria ---
LANGUAGE_CODE = 'es-mx'
TIME_ZONE = 'America/Mexico_City'
USE_I18N = True
USE_TZ = True


# --- Archivos estáticos ---
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'  # donde collectstatic los junta para nginx

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# --- Email (generado por Django; se deja igual) ---
MAILERS = {
    'default': {
        'BACKEND': 'django.core.mail.backends.console.EmailBackend',
    },
}