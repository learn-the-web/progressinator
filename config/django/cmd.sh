#!/usr/bin/env bash

EXTRA_ARGS=""

if [ $DJANGO_SETTINGS_MODULE == "config.settings.dev" ]; then
  EXTRA_ARGS="--reload"
fi

python manage.py collectstatic --no-input
gunicorn $EXTRA_ARGS -t 3600 --bind :8000 --chdir /app config.wsgi:application
