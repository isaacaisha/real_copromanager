# -*- encoding: utf-8 -*- apps/dashboard/urls.py

"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path

#from .views import user_profile, user_update, user_search


urlpatterns = [

    ## Matches any html file
    ##re_path(r'^.*\.*', dashboard, name='dashboard'),

    #path('user-profile/<int:user_id>/', user_profile, name='user-profile'),

    #path('update-profile/', update_profile, name='update-profile'),  # For updating the current user's profile
    #path('update-profile/<int:user_id>/', update_profile, name='update-profile'),  # For Superadmin to update other users

    ## URLs for Search Bar 
    #path('user-search/', user_search, name='user-search'),

]
