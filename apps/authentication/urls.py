# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path
from .views import (
    register_user, login_view, logout_view,
    dashboard_superadmin, customize_license, license_detail,
    dashboard_syndic, dashboard_coproprietaire, dashboard_prestataire,
    delete_syndic, delete_coproprietaire, delete_prestataire
    )


urlpatterns = [
    path('login/', login_view, name="login"),
    path('register/', register_user, name="register"),
    path("logout/", logout_view, name="logout"),

    path('dashboard-superadmin/', dashboard_superadmin, name='dashboard-superadmin'),
    path('customize-license/<int:license_id>/', customize_license, name='customize-license'),

    path('license-detail/<int:license_id>/', license_detail, name='license-detail'),

    path('dashboard-syndic/<int:syndic_id>/', dashboard_syndic, name='dashboard-syndic'),
    path('dashboard-coproprietaire/', dashboard_coproprietaire, name='dashboard-coproprietaire'),
    path('dashboard-prestataire/', dashboard_prestataire, name='dashboard-prestataire'),
    
    # Delete operations for syndic, coproprietaire, prestataire
    path('delete-syndic/<int:syndic_id>/', delete_syndic, name='delete-syndic'),
    path('delete/coproprietaire/<int:coproprietaire_id>/', delete_coproprietaire, name='delete-coproprietaire'),
    path('delete/prestataire/<int:prestataire_id>/', delete_prestataire, name='delete-prestataire'),
]
