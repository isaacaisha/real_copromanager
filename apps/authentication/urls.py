# -*- encoding: utf-8 -*- apps/authentication/urls.py
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path

from .views import (
    ResetPasswordView, CustomPasswordResetConfirmView, CustomPasswordResetCompleteView,
    register_supersyndic, login_supersyndic,
    register_user, login_view, logout_view, update_profile,
    delete_supersyndic, delete_syndic, delete_coproprietaire, delete_prestataire
    )

from apps.dashboard.views import (
    user_search, user_profile,
    dashboard_superadmin, customize_license, license_detail, dashboard_supersyndic,
    dashboard_syndic, dashboard_coproprietaire, dashboard_prestataire,
    gestion_supersyndic, gestion_syndic, gestion_coproprietaire, gestion_prestataire
    )


urlpatterns = [

    path('login/', login_view, name="login"),
    path('register/', register_user, name="register"),
    path("logout/", logout_view, name="logout"),

    # URLs for Password Reset
    path('password_reset/', ResetPasswordView.as_view(), name='password_reset'),
    path('password-reset-confirm/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('password-reset-complete/', CustomPasswordResetCompleteView.as_view(),
         name='password_reset_complete'),

    # URLs for Dashboard Super Syndic
    path('register-supersyndic/<int:syndic_id>/', register_supersyndic, name='register-supersyndic'),
    path('login-supersyndic/<int:supersyndic_id>/', login_supersyndic, name='login-supersyndic'),

    # URLs for Search Bar 
    path('user-search/', user_search, name='user-search'),
    # URLs for User & Update Profile 
    path('user-profile/<int:user_id>/', user_profile, name='user-profile'),
    path('update-profile/', update_profile, name='update-profile'),  # For updating the current user's profile
    path('update-profile/<int:user_id>/', update_profile, name='update-profile-with-id'),  # For Superadmin to update other users

    # Delete operations for syndic, supersyndic, coproprietaire, prestataire
    path('delete-syndic/<int:syndic_id>/', delete_syndic, name='delete-syndic'),
    path('delete-supersyndic/<int:supersyndic_id>/', delete_supersyndic, name='delete-supersyndic'),
    path('delete-coproprietaire/<int:coproprietaire_id>/', delete_coproprietaire, name='delete-coproprietaire'),
    path('delete-prestataire/<int:prestataire_id>/', delete_prestataire, name='delete-prestataire'),

    # URLs for Dashboard User
    path('dashboard-superadmin/', dashboard_superadmin, name='dashboard-superadmin'),
    path('customize-license/<int:license_id>/', customize_license, name='customize-license'),

    path('license-detail/<int:license_id>/', license_detail, name='license-detail'),

    path('gestion-supersyndic/', gestion_supersyndic, name='gestion-supersyndic'),
    path('gestion-syndic/', gestion_syndic, name='gestion-syndic'),
    path('gestion-coproprietaire/', gestion_coproprietaire, name='gestion-coproprietaire'),
    path('gestion-prestataire/', gestion_prestataire, name='gestion-prestataire'),

    path('dashboard-supersyndic/<int:supersyndic_id>/', dashboard_supersyndic, name='dashboard-supersyndic'),
    path('dashboard-syndic/<int:syndic_id>/', dashboard_syndic, name='dashboard-syndic'),
    path('dashboard-coproprietaire/<int:coproprietaire_id>/', dashboard_coproprietaire, name='dashboard-coproprietaire'),
    path('dashboard-prestataire/<int:prestataire_id>/', dashboard_prestataire, name='dashboard-prestataire'),

]
