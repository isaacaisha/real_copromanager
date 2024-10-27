# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path
from .views import (
    register_user, login_view, logout_view,
    delete_syndic, delete_coproprietaire, delete_prestataire
    )
from . import auth_views  
from apps.home.views import (
    user_search, user_profile,
    dashboard_superadmin, customize_license, license_detail,
    dashboard_syndic, dashboard_coproprietaire, dashboard_prestataire,
    gestion_syndic, gestion_coproprietaire, gestion_prestataire
    )


urlpatterns = [

    path('login/', login_view, name="login"),
    path('register/', register_user, name="register"),
    path("logout/", logout_view, name="logout"),

    # URLs for Password Reset
    path('password_reset/', auth_views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # URLs for Search Bar 
    path('user-search/', user_search, name='user-search'),
    # URLs for User Profile 
    path('user/profile/<int:user_id>/', user_profile, name='user-profile'),

    # URLs for Dashboard 
    path('dashboard-superadmin/', dashboard_superadmin, name='dashboard-superadmin'),
    path('customize-license/<int:license_id>/', customize_license, name='customize-license'),

    path('license-detail/<int:license_id>/', license_detail, name='license-detail'),

    path('gestion-syndic/', gestion_syndic, name='gestion-syndic'),
    path('gestion-coproprietaire/', gestion_coproprietaire, name='gestion-coproprietaire'),
    path('gestion-prestataire/', gestion_prestataire, name='gestion-prestataire'),

    path('dashboard-syndic/<int:syndic_id>/', dashboard_syndic, name='dashboard-syndic'),
    path('dashboard-coproprietaire/<int:coproprietaire_id>/', dashboard_coproprietaire, name='dashboard-coproprietaire'),
    path('dashboard-prestataire/<int:prestataire_id>/', dashboard_prestataire, name='dashboard-prestataire'),
    
    # Delete operations for syndic, coproprietaire, prestataire
    path('delete-syndic/<int:syndic_id>/', delete_syndic, name='delete-syndic'),
    path('delete/coproprietaire/<int:coproprietaire_id>/', delete_coproprietaire, name='delete-coproprietaire'),
    path('delete/prestataire/<int:prestataire_id>/', delete_prestataire, name='delete-prestataire'),

]
