# -*- encoding: utf-8 -*- apps/authentication/urls.py
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path

from .views import (
    ResetPasswordView, CustomPasswordResetConfirmView, CustomPasswordResetCompleteView,
    register_supersyndic, login_supersyndic,
    register_user, login_view, logout_view, update_profile,
    delete_residence, delete_supersyndic, delete_syndic, delete_coproprietaire, delete_prestataire
    )

from apps.dashboard.views import (
    user_search, user_profile,
    dashboard_superadmin, customize_license, license_detail, create_residence, update_residence, residence_detail,
    assign_syndic_to_residence, remove_syndic_from_residence, remove_user_from_residence,
    associate_to_residence, associate_to_syndicate,
    dashboard_supersyndic, dashboard_syndic, dashboard_coproprietaire, dashboard_prestataire,
    gestion_residence, gestion_supersyndic, gestion_syndic, gestion_coproprietaire, gestion_prestataire
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
    path('update-profile/<int:user_id>/', update_profile, name='update-profile'),  # For Superadmin to update other users

    # Delete operations for syndic, supersyndic, coproprietaire, prestataire
    path('delete-residence/<int:residence_id>/', delete_residence, name='delete-residence'),
    path('delete-syndic/<int:syndic_id>/', delete_syndic, name='delete-syndic'),
    path('delete-supersyndic/<int:supersyndic_id>/', delete_supersyndic, name='delete-supersyndic'),
    path('delete-coproprietaire/<int:coproprietaire_id>/', delete_coproprietaire, name='delete-coproprietaire'),
    path('delete-prestataire/<int:prestataire_id>/', delete_prestataire, name='delete-prestataire'),

    # URLs for Dashboard User
    path('dashboard-superadmin/<int:superadmin_id>/', dashboard_superadmin, name='dashboard-superadmin'),
    path('customize-license/<int:license_id>/', customize_license, name='customize-license'),
    path('license-detail/<int:license_id>/', license_detail, name='license-detail'),

    # URLs for Residence
    path('create-residence/<int:user_id>/', create_residence, name='create-residence'),
    path('update-residence/<int:residence_id>/', update_residence, name='update-residence'), 
    path('residence-detail/<int:residence_id>/', residence_detail, name='residence-detail'),

    # URLs for Assign User
    path('assign-syndic/', assign_syndic_to_residence, name='assign-syndic'),
    path('associate-to-residence/', associate_to_residence, name='associate-to-residence'),
    path('associate-to-syndicate/', associate_to_syndicate, name='associate-to-syndicate'),

    # URLs for Remove User Assignement
    path('remove-syndic/', remove_syndic_from_residence, name='remove-syndic'),
    path('residence/<int:residence_id>/remove-user/<str:role>/<int:user_id>/', remove_user_from_residence, name='remove-user-from-residence'),

    # URLs for Gestion User
    path('gestion-residence/', gestion_residence, name='gestion-residence'),
    path('gestion-syndic/', gestion_syndic, name='gestion-syndic'),
    path('gestion-supersyndic/', gestion_supersyndic, name='gestion-supersyndic'),
    path('gestion-coproprietaire/', gestion_coproprietaire, name='gestion-coproprietaire'),
    path('gestion-prestataire/', gestion_prestataire, name='gestion-prestataire'),

    # URLs for Dashboard User
    path('dashboard-supersyndic/<int:supersyndic_id>/', dashboard_supersyndic, name='dashboard-supersyndic'),
    path('dashboard-syndic/<int:syndic_id>/', dashboard_syndic, name='dashboard-syndic'),
    path('dashboard-coproprietaire/<int:coproprietaire_id>/', dashboard_coproprietaire, name='dashboard-coproprietaire'),
    path('dashboard-prestataire/<int:prestataire_id>/', dashboard_prestataire, name='dashboard-prestataire'),

]
