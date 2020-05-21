"""Define the production environment settings."""

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from .base import *  # noqa: F403
from .base import env


SENTRY_DSN = env("SENTRY_DSN")
sentry_sdk.init(dsn=SENTRY_DSN, integrations=[DjangoIntegration()])


ALLOWED_HOSTS += [  # noqa: F405
    env("DJANGO_ALLOWED_HOST"),
]
