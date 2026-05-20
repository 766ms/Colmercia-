"""
Django settings for config project.
"""

from pathlib import Path
import os
from urllib.parse import urlparse, parse_qsl
from dotenv import load_dotenv

# ─────────────────────────────────────────────
# BASE DIR
# ─────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

# ─────────────────────────────────────────────
# CARGA DEL .env
# ─────────────────────────────────────────────
load_dotenv(BASE_DIR / ".env")

# ─────────────────────────────────────────────
# SEGURIDAD BÁSICA
# ─────────────────────────────────────────────
SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise Exception("❌ SECRET_KEY no se está cargando desde el .env")

DEBUG = os.getenv("DEBUG") == "True"

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# ─────────────────────────────────────────────
# APPS
# ─────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tienda',
]

# ─────────────────────────────────────────────
# MIDDLEWARE  (orden importa: GZip primero, WhiteNoise segundo)
# ─────────────────────────────────────────────
MIDDLEWARE = [
    "django.middleware.gzip.GZipMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = 'config.urls'

# ─────────────────────────────────────────────
# TEMPLATES
# ─────────────────────────────────────────────
# ⚠️ cached.Loader no recarga cambios sin reiniciar.
# En desarrollo (DEBUG=True) usa APP_DIRS en su lugar.
if DEBUG:
    TEMPLATES = [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [BASE_DIR / "templates"],
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
else:
    TEMPLATES = [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [BASE_DIR / "templates"],
            "OPTIONS": {
                "context_processors": [
                    "django.template.context_processors.debug",
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                ],
                "loaders": [
                    ("django.template.loaders.cached.Loader", [
                        "django.template.loaders.filesystem.Loader",
                        "django.template.loaders.app_directories.Loader",
                    ]),
                ],
            },
        },
    ]

WSGI_APPLICATION = 'config.wsgi.application'

# ─────────────────────────────────────────────
# BASE DE DATOS
# ─────────────────────────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    tmpPostgres = urlparse(DATABASE_URL)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': tmpPostgres.path.lstrip('/'),
            'USER': tmpPostgres.username,
            'PASSWORD': tmpPostgres.password,
            'HOST': tmpPostgres.hostname,
            'PORT': tmpPostgres.port or 5432,
            'CONN_MAX_AGE': 60,
        }
    }
    if tmpPostgres.query:
        DATABASES['default']['OPTIONS'] = dict(parse_qsl(tmpPostgres.query))
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
            'CONN_MAX_AGE': 60,
        }
    }

# ─────────────────────────────────────────────
# CACHÉ EN MEMORIA
# ─────────────────────────────────────────────
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "colmercia-cache",
        "OPTIONS": {
            "MAX_ENTRIES": 1000,
        },
    }
}

# ─────────────────────────────────────────────
# SESIONES
# ─────────────────────────────────────────────
SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"

# ─────────────────────────────────────────────
# VALIDACIÓN PASSWORD
# ─────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ─────────────────────────────────────────────
# INTERNACIONALIZACIÓN
# ─────────────────────────────────────────────
LANGUAGE_CODE = 'es-co'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

# ─────────────────────────────────────────────
# ARCHIVOS ESTÁTICOS
# ─────────────────────────────────────────────
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ─────────────────────────────────────────────
# MEDIA (IMÁGENES)
# ─────────────────────────────────────────────
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ─────────────────────────────────────────────
# CONFIGURACIÓN FINAL
# ─────────────────────────────────────────────
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'tienda.Usuario'
LOGIN_URL = 'landing'
SESSION_SAVE_EVERY_REQUEST = True