# For live applications

release: python manage.py migrate

web: gunicorn --config=python:config.gunicorn config.wsgi:application
