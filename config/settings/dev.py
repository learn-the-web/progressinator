"""Define the development environment settings."""

from .base import *  # noqa: F403

env = environ.Env()  # noqa: F405


def show_toolbar(request):
    """
    Determine if the Django Debug Toolbar should be render into the HTML.

    Prevent the toolbar from rendering in AJAX responses.
    """
    if request.is_ajax():
        return False
    return True


ALLOWED_HOSTS += [  # noqa: F405
    "progressinator.dev",
    "localhost",
    "0.0.0.0",
    "127.0.0.1",
    "[::1]",
]

LOGGING["root"] = {"level": "DEBUG"}  # noqa: F405

if DEBUG:  # noqa: F405
    INSTALLED_APPS += ["debug_toolbar"]  # noqa: F405
    MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]  # noqa: F405

    available_debug_toolbar_panels = {
        "logging": "debug_toolbar.panels.logging.LoggingPanel",
        "versions": "debug_toolbar.panels.versions.VersionsPanel",
        "timer": "debug_toolbar.panels.timer.TimerPanel",
        "settings": "debug_toolbar.panels.settings.SettingsPanel",
        "headers": "debug_toolbar.panels.headers.HeadersPanel",
        "request": "debug_toolbar.panels.request.RequestPanel",
        "sql": "debug_toolbar.panels.sql.SQLPanel",
        "staticfiles": "debug_toolbar.panels.staticfiles.StaticFilesPanel",
        "templates": "debug_toolbar.panels.templates.TemplatesPanel",
        "cache": "debug_toolbar.panels.cache.CachePanel",
        "signals": "debug_toolbar.panels.signals.SignalsPanel",
        "redirects": "debug_toolbar.panels.redirects.RedirectsPanel",
        "profiling": "debug_toolbar.panels.profiling.ProfilingPanel",
    }

    DEBUG_TOOLBAR_PANELS_TO_LOAD = env.str("DEBUG_TOOLBAR_PANELS", default="")
    DEBUG_TOOLBAR_PANELS = []

    for key, panel in available_debug_toolbar_panels.items():
        if key in DEBUG_TOOLBAR_PANELS_TO_LOAD or not DEBUG_TOOLBAR_PANELS_TO_LOAD:
            DEBUG_TOOLBAR_PANELS.append(panel)

    DEBUG_TOOLBAR_CONFIG = {
        "SHOW_TOOLBAR_CALLBACK": "config.settings.dev.show_toolbar",
    }
