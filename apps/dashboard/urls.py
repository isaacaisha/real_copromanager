# -*- encoding: utf-8 -*- apps/dashboard/urls.py

"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path

#from apps.dashboard.views import (
#    dashboard,
#    user_search, user_profile,
#    dashboard_superadmin, customize_license, license_detail, dashboard_supersyndic,
#    dashboard_syndic, dashboard_coproprietaire, dashboard_prestataire,
#    gestion_supersyndic, gestion_syndic, gestion_coproprietaire, gestion_prestataire
#    )


urlpatterns = [

    # Matches any html file
    #re_path(r'^.*\.*', dashboard, name='dashboard'),

    ## URLs for Dashboard User
    #path('dashboard-superadmin/', dashboard_superadmin, name='dashboard-superadmin'),
    #path('customize-license/<int:license_id>/', customize_license, name='customize-license'),
#
    #path('license-detail/<int:license_id>/', license_detail, name='license-detail'),
#
    #path('gestion-supersyndic/', gestion_supersyndic, name='gestion-supersyndic'),
    #path('gestion-syndic/', gestion_syndic, name='gestion-syndic'),
    #path('gestion-coproprietaire/', gestion_coproprietaire, name='gestion-coproprietaire'),
    #path('gestion-prestataire/', gestion_prestataire, name='gestion-prestataire'),
#
    #path('dashboard-supersyndic/<int:supersyndic_id>/', dashboard_supersyndic, name='dashboard-supersyndic'),
    #path('dashboard-syndic/<int:syndic_id>/', dashboard_syndic, name='dashboard-syndic'),
    #path('dashboard-coproprietaire/<int:coproprietaire_id>/', dashboard_coproprietaire, name='dashboard-coproprietaire'),
    #path('dashboard-prestataire/<int:prestataire_id>/', dashboard_prestataire, name='dashboard-prestataire'),
    #
    ## URLs for Search Bar 
    #path('user-search/', user_search, name='user-search'),
    ## URLs for User Profile 
    #path('user/profile/<int:user_id>/', user_profile, name='user-profile'),

]
