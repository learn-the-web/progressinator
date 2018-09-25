import os
import environ


env = environ.Env()


DEBUG = False


root = environ.Path(__file__) - 3
SITE_ROOT = root()
APPS_DIR = root.path('progress/')
BASE_DIR = SITE_ROOT # For Heroku


ALLOWED_HOSTS = [
    'floating-tundra-76216.herokuapp.com',
]


DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.postgres',
]
THIRD_PARTY_APPS = [
    'gunicorn',
    'localflavor',
    'social_django',
]
LOCAL_APPS = [
    'progress.core',
]
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS


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


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            str(APPS_DIR.path('templates')),
            str(APPS_DIR.path('patterns')),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]


ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'
APPEND_SLASH = True


DATABASES = {
    'default': env.db(),
}
DATABASES['default']['CONN_MAX_AGE'] = env.int('CONN_MAX_AGE', default=500)


SECRET_KEY =  env('DJANGO_SECRET_KEY')

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


LANGUAGE_CODE = 'en-ca'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True
PHONENUMBER_DB_FORMAT = 'E164'
PHONENUMBER_DEFAULT_REGION = 'CA'


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'ERROR'),
        },
    },
}


STATIC_URL = '/public/'
STATIC_ROOT = str(root.path('public'))
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATICFILES_DIRS = (
    ('core', str(root.path('public-dist'))),
)


ADMIN_URL = env('DJANGO_ADMIN_URL')


AUTHENTICATION_BACKENDS = (
    'social_core.backends.github.GithubOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/sign-in'
LOGOUT_REDIRECT_URL = '/sign-in'

SOCIAL_AUTH_POSTGRES_JSONFIELD = True
SOCIAL_AUTH_GITHUB_KEY = '3752b529955d95f467e7'
SOCIAL_AUTH_GITHUB_SECRET = '2dcce1345f94feddc4f4739f896b9d437566893b'
SOCIAL_AUTH_GITHUB_SCOPE = [
    'read:user',
    'user:email',
]
# SOCIAL_AUTH_USER_MODEL = 'progress.core.models.User'
SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/'
