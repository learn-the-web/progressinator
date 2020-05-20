"""Define the Gunicorn settings for the development environment."""

from .gunicorn import *  # noqa: F401,F403

bind = "0.0.0.0:8000"
preload_app = False  # Reload is incompatible with app preloading
reload = True
timeout = 3600

certfile = "./config/certs/progressinator.dev.pem"
keyfile = "./config/certs/progressinator.dev-key.pem"
pidfile = ".gunicorn.pid"
