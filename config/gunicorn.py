"""
Define the Gunicorn settings for the production environment.

*References:*
- https://devcenter.heroku.com/articles/python-gunicorn
- https://docs.gunicorn.org/en/stable/settings.html
- http://www.pixeldonor.com/2014/jan/10/django-gevent-and-socketio/
- https://medium.com/@bfirsh/squeezing-every-drop-of-performance-out-of-a-django-app-on-heroku-4b5b1e5a3d44
"""

from psycogreen.gevent import patch_psycopg

errorlog = "-"

preload_app = True

worker_class = "gevent"
max_requests = 5000


def post_fork(server, worker):
    """Patch the PostgreSQL `pyscopg` library to use connection pooling with Gevent."""
    patch_psycopg()
