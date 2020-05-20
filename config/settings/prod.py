"""Define the production environment settings."""

from .base import *  # noqa: F403
from .base import env


ALLOWED_HOSTS += [  # noqa: F405
    env("DJANGO_ALLOWED_HOST"),
]
