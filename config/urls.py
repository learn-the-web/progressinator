from django.contrib import admin
from django.urls import include, path
from django.conf.urls import url
from django.conf import settings

urlpatterns = [
    path('', include('progress.core.urls')),
    path(settings.ADMIN_URL, admin.site.urls),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
