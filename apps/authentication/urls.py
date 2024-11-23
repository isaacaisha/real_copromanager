# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path

from .views import (
    ResetPasswordView, CustomPasswordResetConfirmView, CustomPasswordResetCompleteView,
    register_super_syndic, login_super_syndic,
    register_user, login_view, logout_view,
    delete_syndic, delete_super_syndic, delete_coproprietaire, delete_prestataire
    )

from apps.home.views import (
    user_search, user_profile,
    dashboard_superadmin, customize_license, license_detail, dashboard_super_syndic,
    dashboard_syndic, dashboard_coproprietaire, dashboard_prestataire,
    gestion_super_syndic, gestion_syndic, gestion_coproprietaire, gestion_prestataire
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

    # URLs for Dashboard Super User
    path('register-super-syndic/<int:syndic_id>/', register_super_syndic, name='register-super-syndic'),
    path('login-super-syndic/<int:super_syndic_id>/', login_super_syndic, name='login-super-syndic'),

    # URLs for Dashboard User
    path('dashboard-superadmin/', dashboard_superadmin, name='dashboard-superadmin'),
    path('customize-license/<int:license_id>/', customize_license, name='customize-license'),

    path('license-detail/<int:license_id>/', license_detail, name='license-detail'),

    path('gestion-super-syndic/', gestion_super_syndic, name='gestion-super-syndic'),
    path('gestion-syndic/', gestion_syndic, name='gestion-syndic'),
    path('gestion-coproprietaire/', gestion_coproprietaire, name='gestion-coproprietaire'),
    path('gestion-prestataire/', gestion_prestataire, name='gestion-prestataire'),

    path('dashboard-super-syndic/<int:super_syndic_id>/', dashboard_super_syndic, name='dashboard-super-syndic'),
    path('dashboard-syndic/<int:syndic_id>/', dashboard_syndic, name='dashboard-syndic'),
    path('dashboard-coproprietaire/<int:coproprietaire_id>/', dashboard_coproprietaire, name='dashboard-coproprietaire'),
    path('dashboard-prestataire/<int:prestataire_id>/', dashboard_prestataire, name='dashboard-prestataire'),
    
    # Delete operations for syndic, coproprietaire, prestataire
    path('delete-syndic/<int:syndic_id>/', delete_syndic, name='delete-syndic'),
    path('delete-super-syndic/<int:super_syndic_id>/', delete_super_syndic, name='delete-super-syndic'),
    path('delete/coproprietaire/<int:coproprietaire_id>/', delete_coproprietaire, name='delete-coproprietaire'),
    path('delete/prestataire/<int:prestataire_id>/', delete_prestataire, name='delete-prestataire'),

    # URLs for Search Bar 
    path('user-search/', user_search, name='user-search'),
    # URLs for User Profile 
    path('user/profile/<int:user_id>/', user_profile, name='user-profile'),

]
