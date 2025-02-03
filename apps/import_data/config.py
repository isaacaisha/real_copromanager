# -*- encoding: utf-8 -*- apps/dashboard/config.py

"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.apps import AppConfig

class MyConfig(AppConfig):
    name = 'apps.import_data'
    label = 'apps_import_data'
    
#from django.apps import AppConfig
#
#
#class ImportDataConfig(AppConfig):
#    default_auto_field = 'django.db.models.BigAutoField'
#    name = 'import_data'
#