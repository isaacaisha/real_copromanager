# -*- encoding: utf-8 -*- apps/dashboard/admin.py

"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin
from .models import Prestataire

# Register your models here.

admin.site.register(Prestataire)
