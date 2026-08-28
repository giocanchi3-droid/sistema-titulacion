from pathlib import Path

import dj_database_url
from decouple import Csv, config


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config(
    "SECRET_KEY",
    default="clave-insegura-solo-desarrollo",
)

DEBUG = config("DEBUG", default=True, cast=bool)

ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    default="127.0.0.1,localhost",
    cast=Csv(),
)


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "rest_framework",

    "core",
    "estudiantes",
    "procesos",
    "documentos",
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "config.urls"


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


WSGI_APPLICATION = "config.wsgi.application"


DATABASE_URL = config("DATABASE_URL", default="")

if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": config(
                "DB_NAME",
                default="pucetec_titulacion",
            ),
            "USER": config(
                "DB_USER",
                default="postgres",
            ),
            "PASSWORD": config(
                "DB_PASSWORD",
                default="gio2006",
            ),
            "HOST": config(
                "DB_HOST",
                default="127.0.0.1",
            ),
            "PORT": config(
                "DB_PORT",
                default="5432",
            ),
        }
    }


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        ),
    },
]


LANGUAGE_CODE = "es-ec"

TIME_ZONE = "America/Guayaquil"

USE_I18N = True

USE_TZ = True


STATIC_URL = "/static/"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_STORAGE = (
    "whitenoise.storage.CompressedManifestStaticFilesStorage"
)


MEDIA_URL = "/media/"

RENDER = config("RENDER", default=False, cast=bool)
MEDIA_ROOT_CONFIG = config("MEDIA_ROOT", default="")

if MEDIA_ROOT_CONFIG:
    MEDIA_ROOT = Path(MEDIA_ROOT_CONFIG)
elif RENDER:
    MEDIA_ROOT = Path("/var/data/media")
else:
    MEDIA_ROOT = BASE_DIR / "media"


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


LOGIN_URL = "login"

LOGIN_REDIRECT_URL = "core:dashboard"

LOGOUT_REDIRECT_URL = "login"


REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}


# EXCEL_UPLOAD_LIMIT_START
# Tamaño máximo permitido para una matriz Excel: 100 MB.
MAX_EXCEL_UPLOAD_SIZE = 100 * 1024 * 1024

# Margen adicional para el cuerpo completo de la solicitud.
DATA_UPLOAD_MAX_MEMORY_SIZE = 110 * 1024 * 1024

# Archivos mayores a 5 MB se almacenan temporalmente en disco,
# evitando mantener archivos grandes completamente en memoria RAM.
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024
# EXCEL_UPLOAD_LIMIT_END
