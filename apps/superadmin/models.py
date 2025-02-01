# -*- encoding: utf-8 -*- apps/dashboard/forms.py

"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.conf import settings
from django.db import models
from django.utils.translation import gettext as _

from apps.syndic.models import Syndic

from apps.supersyndic.models import SuperSyndic

# Superadmin Model
class Superadmin(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='superadmin_profile',
        null=True,
        blank=True,
        verbose_name=_('User'),
    )
    syndics = models.ManyToManyField(
        Syndic,
        related_name='managed_by_superadmins',
        blank=True,
        verbose_name=_('Syndics'),
    )
    supersyndics = models.ManyToManyField(
        SuperSyndic,
        related_name='managed_by_superadmins',
        blank=True,
        verbose_name=_('SuperSyndics'),
    )
    
    def __str__(self):
        return _("Superadmin: {email}").format(email=self.user.email)


# Licence Base
class LicenseBase(models.Model):
    nom = models.CharField(max_length=255, unique=True, verbose_name=_('Name'))
    fonctionnalites = models.JSONField(verbose_name=_('Features'))
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name=_('Creation Date'))
    
    def __str__(self):
        return self.nom
    

# Custom License for Syndic
class License(models.Model):
    syndic = models.ForeignKey(
        Syndic,
        on_delete=models.CASCADE,
        related_name='syndic_licenses',
        null=True,
        blank=True,
        verbose_name=_('Syndic'),
    )
    supersyndic = models.ForeignKey(
        SuperSyndic,
        on_delete=models.CASCADE,
        related_name='supersyndic_licenses',
        null=True,
        blank=True,
        verbose_name=_('Super Syndic'),
    )
    license_base = models.ForeignKey(
        LicenseBase,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='licenses',
        verbose_name=_('Base License'),
    )
    date_debut = models.DateField(null=True, blank=True, verbose_name=_('Start Date'))
    date_fin = models.DateField(null=True, blank=True, verbose_name=_('End Date'))
    fonctionnalites_personnalisees = models.JSONField(null=True, blank=True, verbose_name=_('Custom Features'))
    est_personnalise = models.BooleanField(default=True, verbose_name=_('Is Custom'))

    def get_fonctionnalites(self):
        if self.est_personnalise and self.fonctionnalites_personnalisees:
            return self.fonctionnalites_personnalisees
        elif self.license_base:
            return self.license_base.fonctionnalites
        return []

    def __str__(self):
        role = self.syndic or self.supersyndic
        return _("License for {role} (from {start} to {end})").format(
            role=role.nom, start=self.date_debut, end=self.date_fin
        )
    