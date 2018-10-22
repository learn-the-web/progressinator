from .base import *
from .base import env


ALLOWED_HOSTS += [
]


# SESSION_COOKIE_DOMAIN = '.learn-the-web.algonquindesign.ca'
# CSRF_COOKIE_DOMAIN = SESSION_COOKIE_DOMAIN
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_AGE = 60 * 60 * 24 * 30

SECURE_SSL_REDIRECT = True
