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
    DJANGO_LOG_LEVEL_APPLICATION=(str, 'INFO'),
    DJANGO_LOG_LEVEL_ACCESS=(str, 'DEBUG'),
    DJANGO_LOG_LEVEL_ERROR=(str, 'ERROR'),
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
    'backoffice.middleware.AccessLogMiddleware',
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
TIME_ZONE     = 'Europe/Paris'
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

LOG_DIR_RAW = env('DJANGO_LOG_DIR')
LOG_DIR = Path(LOG_DIR_RAW) if os.path.isabs(LOG_DIR_RAW) else (BASE_DIR / LOG_DIR_RAW)
LOG_DIR.mkdir(parents=True, exist_ok=True)
APPLICATION_LOG_LEVEL = env('DJANGO_LOG_LEVEL_APPLICATION').upper()
ACCESS_LOG_LEVEL = env('DJANGO_LOG_LEVEL_ACCESS').upper()
ERROR_LOG_LEVEL = env('DJANGO_LOG_LEVEL_ERROR').upper()

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '{levelname} {asctime} {module} {message}',
            'style':  '{',
        },
        'access': {
            'format': '{asctime} {levelname} {message}',
            'style':  '{',
        },
    },
    'handlers': {
        'application_file': {
            'class':     'logging.handlers.RotatingFileHandler',
            'filename':  str(LOG_DIR / 'application.log'),
            'maxBytes':  5 * 1024 * 1024,  # 5 Mo
            'backupCount': 3,
            'formatter': 'standard',
            'level': APPLICATION_LOG_LEVEL,
        },
        'error_file': {
            'class':     'logging.handlers.RotatingFileHandler',
            'filename':  str(LOG_DIR / 'erreur.log'),
            'maxBytes':  5 * 1024 * 1024,  # 5 Mo
            'backupCount': 3,
            'formatter': 'standard',
            'level': ERROR_LOG_LEVEL,
        },
        'access_file': {
            'class':     'logging.handlers.RotatingFileHandler',
            'filename':  str(LOG_DIR / 'acces.log'),
            'maxBytes':  5 * 1024 * 1024,  # 5 Mo
            'backupCount': 3,
            'formatter': 'access',
            'level': ACCESS_LOG_LEVEL,
        },
    },
    'loggers': {
        'django': {
            'handlers': ['application_file', 'error_file'],
            'level': APPLICATION_LOG_LEVEL,
            'propagate': False,
        },
        'django.request': {
            'handlers': ['application_file', 'error_file'],
            'level': APPLICATION_LOG_LEVEL,
            'propagate': False,
        },
        'django.server': {
            'handlers': ['access_file'],
            'level': ACCESS_LOG_LEVEL,
            'propagate': False,
        },
        'backoffice': {
            'handlers': ['application_file', 'error_file'],
            'level': APPLICATION_LOG_LEVEL,
            'propagate': False,
        },
        'core': {
            'handlers': ['application_file', 'error_file'],
            'level': APPLICATION_LOG_LEVEL,
            'propagate': False,
        },
        'access': {
            'handlers': ['access_file'],
            'level': ACCESS_LOG_LEVEL,
            'propagate': False,
        },
    },
}
