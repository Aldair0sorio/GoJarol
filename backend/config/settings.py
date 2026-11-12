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
# Public OAuth audience; empty disables Google sign-in until configured.
GOOGLE_CLIENT_ID = env('GOOGLE_CLIENT_ID', default='')
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
        'accounts.authentication.VerifiedTokenAuthentication',
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


# --- Email: Django 6.1 MAILERS, STARTTLS, no implicit SSL ---
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='Go Jarol <no.reply.trees.25@gmail.com>')
FRONTEND_URL = env('FRONTEND_URL', default='http://localhost:5173')
MAIL_HOST = env('MAIL_HOST', default='')
MAIL_PORT = env.int('MAIL_PORT', default=587)
MAIL_USERNAME = env('MAIL_USERNAME', default='')
MAIL_PASSWORD = env('MAIL_PASSWORD', default='')
MAIL_USE_TLS = env.bool('MAIL_USE_TLS', default=True)
# Development can explicitly use filebased or locmem. Missing SMTP configuration
# never silently substitutes a fake delivery in production.
MAILERS = {
    'default': {
        'BACKEND': env('MAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend'),
        'OPTIONS': {
            'host': MAIL_HOST, 'port': MAIL_PORT, 'username': MAIL_USERNAME,
            'password': MAIL_PASSWORD, 'use_tls': MAIL_USE_TLS, 'use_ssl': False,
            'timeout': 10,
        },
    },
}
if MAILERS['default']['BACKEND'] != 'django.core.mail.backends.smtp.EmailBackend':
    if not DEBUG:
        from django.core.exceptions import ImproperlyConfigured
        raise ImproperlyConfigured('Non-SMTP mail backends require DEBUG=True.')
    MAILERS['default']['OPTIONS'] = {}
    if MAILERS['default']['BACKEND'] == 'django.core.mail.backends.filebased.EmailBackend':
        MAILERS['default']['OPTIONS'] = {'file_path': str(BASE_DIR / 'dev-emails')}
