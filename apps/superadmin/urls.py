# -*- encoding: utf-8 -*- apps/dashboard/urls.py

"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path

#from .views import dashboard_superadmin, customize_license, license_detail


urlpatterns = [

    # Matches any html file
    #re_path(r'^.*\.*', dashboard, name='dashboard'),

    ## URLs for Dashboard superadmin
    #path('dashboard-superadmin/', dashboard_superadmin, name='dashboard-superadmin'),

    ## URLs for Dashboard license
    #path('customize-license/<int:license_id>/', customize_license, name='customize-license'),
    #path('license-detail/<int:license_id>/', license_detail, name='license-detail'),

]
