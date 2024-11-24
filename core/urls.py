# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin
from django.urls import path, include
from two_factor.urls import urlpatterns as tf_urls

from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),          # Django admin route
    path("", include("apps.authentication.urls")), # Auth routes - login / register
    path('', include(tf_urls)),  # Include 2FA URLs
    path("", include("apps.home.urls")),             # UI Kits Html files
    #path("", include("apps.dashboard.urls"))             # UI Kits Html files
]

if settings.DEBUG:  # Serve media files only during development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
