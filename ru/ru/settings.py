"""
Django settings for ru project.
"""
import environ
import os
from pathlib import Path

# ── Répertoires ───────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

# ── django-environ ────────────────────────────────────────────
env = environ.Env(
    DJANGO_DEBUG=(bool, False),
    DJANGO_ALLOWED_HOSTS=(list, ['127.0.0.1', 'localhost']),
    DJANGO_CSRF_TRUSTED_ORIGINS=(list, []),
    DATABASE_URL=(str, f'sqlite:///{BASE_DIR / "db.sqlite3"}'),
    DJANGO_LOG_DIR=(str, str(BASE_DIR / 'logs')),
)

environ.Env.read_env(BASE_DIR.parent / '.env')

# ── Sécurité ──────────────────────────────────────────────────
SECRET_KEY = env('DJANGO_SECRET_KEY')
DEBUG       = env('DJANGO_DEBUG')
ALLOWED_HOSTS           = env('DJANGO_ALLOWED_HOSTS')
CSRF_TRUSTED_ORIGINS    = env('DJANGO_CSRF_TRUSTED_ORIGINS')


# ── Applications ──────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core.apps.CoreConfig',
    'backoffice.apps.BackofficeConfig',
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

ROOT_URLCONF = 'ru.urls'

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

WSGI_APPLICATION = 'ru.wsgi.application'

# ── Base de données ───────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ── Validation des mots de passe ──────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ── Internationalisation ──────────────────────────────────────
LANGUAGE_CODE = 'fr'
TIME_ZONE     = 'UTC'
USE_I18N      = True
USE_TZ        = True

# ── Fichiers statiques ────────────────────────────────────────
STATIC_URL  = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# ── Authentification ──────────────────────────────────────────
LOGIN_URL = 'backoffice:login'

# ── Version affichée (sidebar, etc.) ──────────────────────────
APPLICATION_RELEASE = 'v2.0'

# ── Logging ───────────────────────────────────────────────────

LOG_DIR = Path(env('DJANGO_LOG_DIR'))
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style':  '{',
        },
    },
    'handlers': {
        'console': {
            'class':     'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class':     'logging.handlers.RotatingFileHandler',
            'filename':  str(LOG_DIR / 'django.log'),
            'maxBytes':  5 * 1024 * 1024,  # 5 Mo
            'backupCount': 3,
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level':    'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level':    'WARNING' if not DEBUG else 'INFO',
            'propagate': False,
        },
        'backoffice': {
            'handlers': ['console', 'file'],
            'level':    'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
    },
}
