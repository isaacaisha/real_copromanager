# -*- encoding: utf-8 -*- apps/dashboard/forms.py

"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.conf import settings
from django.db import models
from django.utils.translation import gettext as _

from apps.residence.models import Residence

from apps.syndic.models import Syndic

from apps.supersyndic.models import SuperSyndic

# Provider Information
class Prestataire(models.Model):
    nom = models.CharField(max_length=255, verbose_name=_('Name'))
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='prestataire_profile',
        null=True,
        blank=True,
        verbose_name=_('User'),
    )
    email = models.EmailField(verbose_name=_('Email'))
    syndic = models.ManyToManyField(Syndic, verbose_name=_('Syndic'), blank=True, related_name='syndic_prestataires')
    supersyndic = models.ManyToManyField(SuperSyndic, verbose_name=_('SuperSyndic'), blank=True, related_name='supersyndic_prestataires')
    residence = models.ManyToManyField(Residence, verbose_name=_('Residences'), blank=True, related_name='prestataire_residences')

    def __str__(self):
        return self.user.nom if self.user else self.nom
    