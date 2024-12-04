# -*- encoding: utf-8 -*- apps/dashboard/config.py

"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.apps import AppConfig


class MyConfig(AppConfig):
    name = 'apps.dashboard'
    label = 'apps_dashboard'

#from django.apps import AppConfig
#
#class DashboardConfig(AppConfig):
#    default_auto_field = 'django.db.models.BigAutoField'
#    name = 'apps.dashboard'
#    