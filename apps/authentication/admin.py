# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin
from .models import CustomUser, Superadmin, Syndic, Coproprietaire, Prestataire, Immeuble, Appartement, LicenseBase, License

# Register your models here.

admin.site.register(CustomUser)
admin.site.register(Superadmin)
admin.site.register(Syndic)
admin.site.register(Coproprietaire)
admin.site.register(Prestataire)
admin.site.register(Immeuble)
admin.site.register(Appartement)
admin.site.register(LicenseBase)
admin.site.register(License)
