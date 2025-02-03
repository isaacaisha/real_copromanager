# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

# from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import set_language

from django.contrib import admin
from django.urls import path, include
from two_factor.urls import urlpatterns as tf_urls

from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls), # Django admin route
    path('', include(tf_urls)), # Include 2FA URLs
    path('set_language/', set_language, name='set_language'),
    path("", include("apps.authentication.urls")), # Auth routes - login / register
    path("", include("apps.home.urls")), # UI Kits Html files
    path("", include("apps.superadmin.urls")),
    path("", include("apps.syndic.urls")),
    path("", include("apps.supersyndic.urls")),
    path("", include("apps.coproprietaire.urls")),
    path("", include("apps.prestataire.urls")),
    path("", include("apps.residence.urls")),
    path("", include("apps.association.urls")),
    path("", include("apps.import_data.urls")),
]

# urlpatterns += i18n_patterns(
#     # Translated URLs
#     path('set_language/', set_language, name='set_language'),
# )

if settings.DEBUG:  # Serve media files only during development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
