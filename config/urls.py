from django.urls import include, path
from django.conf.urls import url
from django.conf import settings

urlpatterns = [
    path("", include("progressinator.core.urls")),
    path("", include("social_django.urls", namespace="social")),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [url(r"^__debug__/", include(debug_toolbar.urls)),] + urlpatterns
