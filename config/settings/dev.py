from .base import *
from .base import env
# from debug_toolbar.panels.logging import collector


def show_toolbar(request):
    if request.is_ajax():
        return False
    return True


DEBUG = True


ALLOWED_HOSTS += [
    'localhost',
    '0.0.0.0',
    '127.0.0.1',
    '[::1]',
]


INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': 'config.settings.dev.show_toolbar',
}

LOGGING['incremental'] = True
LOGGING['root'] = {
    'level' : 'DEBUG'
}
