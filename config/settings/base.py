"""Define the shared environment settings."""

import json
import locale

import environ


env = environ.Env()
DEBUG = env.bool("DJANGO_DEBUG", default=False)


root = environ.Path(__file__) - 3
SITE_ROOT = root()
APPS_DIR = root.path("progressinator/")
BASE_DIR = SITE_ROOT  # For Heroku

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
APPEND_SLASH = True

ALLOWED_HOSTS = []


##################################################
# APPS
##################################################

DJANGO_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django.contrib.postgres",
]
THIRD_PARTY_APPS = [
    "gunicorn",
    "localflavor",
    "social_django",
    "rest_framework",
    "rest_framework.authtoken",
    "impersonate",
]
LOCAL_APPS = [
    "progressinator.core",
]
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS


##################################################
# MIDDLEWARE
##################################################

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "impersonate.middleware.ImpersonateMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


##################################################
# TEMPLATES
##################################################

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [str(APPS_DIR.path("templates")), str(APPS_DIR.path("patterns")),],
        "OPTIONS": {
            "builtins": ["django.templatetags.static"],
            "loaders": [
                (
                    "django.template.loaders.cached.Loader",
                    [
                        "django.template.loaders.filesystem.Loader",
                        "django.template.loaders.app_directories.Loader",
                    ],
                ),
            ],
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect",
            ],
        },
    },
]

##################################################
# LOGGING
##################################################

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler",},
        "file": {"class": "logging.FileHandler", "filename": "log.json",},
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "WARNING" if DEBUG else "ERROR",
            "propagate": True,
        },
        "django.template": {
            "handlers": ["console"],
            "level": "WARNING" if DEBUG else "ERROR",
            "propagate": True,
        },
    },
}


##################################################
# DATABASES
##################################################

DATABASES = {
    "default": env.db(),
}
# Setup for Gevent connection pooling
# https://github.com/jneight/django-db-geventpool
# https://medium.com/@bfirsh/squeezing-every-drop-of-performance-out-of-a-django-app-on-heroku-4b5b1e5a3d44
DATABASES["default"]["ENGINE"] = "django_db_geventpool.backends.postgresql_psycopg2"
DATABASES["default"]["CONN_MAX_AGE"] = env.int("CONN_MAX_AGE", default=0)
DATABASES["default"]["OPTIONS"] = {
    "MAX_CONNS": 24,
}


##################################################
# LOCALIZATION
##################################################

locale.setlocale(locale.LC_ALL, "en_CA.UTF-8")
LANGUAGE_CODE = "en"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True
PHONENUMBER_DB_FORMAT = "E164"
PHONENUMBER_DEFAULT_REGION = "CA"


##################################################
# STATIC FILES
##################################################

STATIC_URL = "/public/"
STATIC_ROOT = str(root.path("public"))
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
STATICFILES_DIRS = (("core", str(root.path("public-dist"))),)


##################################################
# SECURITY
##################################################

SECRET_KEY = env("DJANGO_SECRET_KEY")

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",},
]

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "social_core.backends.github.GithubOAuth2",
)

LOGIN_REDIRECT_URL = "/"
LOGIN_URL = "/auth/sign-in"
LOGOUT_REDIRECT_URL = "/auth/sign-in"

SECURE_SSL_REDIRECT = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_HSTS_SECONDS = 31536000
X_FRAME_OPTIONS = "DENY"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = "Lax"  # Necessary for Social Auth to work properly
SESSION_ENGINE = "django.contrib.sessions.backends.db"
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = "Strict"

SOCIAL_AUTH_POSTGRES_JSONFIELD = True
SOCIAL_AUTH_GITHUB_KEY = env("SOCIAL_AUTH_GITHUB_KEY")
SOCIAL_AUTH_GITHUB_SECRET = env("SOCIAL_AUTH_GITHUB_SECRET")
SOCIAL_AUTH_GITHUB_SCOPE = [
    "read:user",
    "user:email",
]
SOCIAL_AUTH_LOGIN_REDIRECT_URL = "/"

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ),
}


##################################################
# APPLICATION
##################################################

MARKBOT = {
    "DESKTOP_VERSION": "8.0.4",
    "ONLINE_VERSION": "1.0.0",
    "PASSCODE_HASH": env("MARKBOT_PASSCODE_HASH"),
}

COURSES = {
    "SELF_DIRECTED_ID": 0,
}

with open(str(root.path("package.json"))) as json_data:
    APP_PKG = json.load(json_data)

SRI_HASHES = {}
try:
    with open("config/sri.json", "r") as sri:
        SRI_HASHES = json.load(sri)
except Exception as e:
    from sentry_sdk import capture_exception

    capture_exception(e)
