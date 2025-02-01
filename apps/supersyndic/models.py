# -*- encoding: utf-8 -*- apps/dashboard/forms.py

"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.conf import settings
from django.db import models
from django.utils.translation import gettext as _


class SuperSyndic(models.Model):
    nom = models.CharField(max_length=255, verbose_name=_('Name'))
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='supersyndic_profile',
        null=True,
        blank=True,
        verbose_name=_('User'),
    )
    email = models.EmailField(verbose_name=_('Email'))

    def __str__(self):
        return self.user.nom if self.user else self.nom
    