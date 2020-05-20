"""Define the global URLs for the progressinator project."""

from django.conf import settings
from django.conf.urls import url
from django.urls import include, path

urlpatterns = [
    url(r"^impersonate/", include("impersonate.urls")),
    path("", include("progressinator.core.urls")),
    path("", include("social_django.urls", namespace="social")),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [url(r"^__debug__/", include(debug_toolbar.urls)),] + urlpatterns
