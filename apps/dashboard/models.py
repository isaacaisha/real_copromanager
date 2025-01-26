# -*- encoding: utf-8 -*- apps/dashboard/forms.py

"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.conf import settings
from django.db import models
from django.utils.translation import gettext as _

from apps.authentication.models import CustomUser

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
        'Syndic',
        related_name='managed_by_superadmins',
        blank=True,
        verbose_name=_('Syndics'),
    )
    supersyndics = models.ManyToManyField(
        'SuperSyndic',
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
        'Syndic',
        on_delete=models.CASCADE,
        related_name='syndic_licenses',
        null=True,
        blank=True,
        verbose_name=_('Syndic'),
    )
    supersyndic = models.ForeignKey(
        'SuperSyndic',
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


# Syndic Information
class Syndic(models.Model):
    nom = models.CharField(max_length=255, verbose_name=_('Name'))
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='syndic_profile',
        null=True,
        blank=True,
        verbose_name=_('User'),
    )
    email = models.EmailField(verbose_name=_('Email'))
    superadmin = models.ForeignKey(
        'SuperAdmin',
        on_delete=models.CASCADE,
        related_name='superadmin_syndics',
        null=True,
        blank=True,
        verbose_name=_('SuperAdmin'),
    )

    def __str__(self):
        return self.user.nom


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
    superadmin = models.ForeignKey(
        'SuperAdmin',
        on_delete=models.CASCADE,
        related_name='superadmin_supersyndics',
        null=True,
        blank=True,
        verbose_name=_('SuperAdmin'),
    )

    def __str__(self):
        return self.user.nom


# Building Information
class Residence(models.Model):
    nom = models.CharField(max_length=255, verbose_name=_('Name'))
    adresse = models.TextField(verbose_name=_('Address'))
    nombre_appartements = models.IntegerField(verbose_name=_('Number of Apartments'))
    superficie_totale = models.FloatField(verbose_name=_('Total Area'))
    date_construction = models.DateField(verbose_name=_('Construction Date'))
    nombre_etages = models.IntegerField(verbose_name=_('Number of Floors'))
    zones_communes = models.TextField(verbose_name=_('Common Areas'))  # Example: "Hall, Garden, Parking"
    date_dernier_controle = models.DateField(null=True, blank=True, verbose_name=_('Last Inspection Date'))
    type_chauffage = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('Heating Type'))
    syndic = models.ManyToManyField(Syndic, verbose_name=_('Syndic'), blank=True, related_name='syndic_residences')
    supersyndic = models.ManyToManyField(SuperSyndic, verbose_name=_('SuperSyndic'), blank=True, related_name='supersyndic_residences')
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_residences")

    def __str__(self):
        return _("Building {name} ({address})").format(name=self.nom, address=self.adresse)


# Co-owner Information
class Coproprietaire(models.Model):
    nom = models.CharField(max_length=255, verbose_name=_('Name'))
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='coproprietaire_profile',
        null=True,
        blank=True,
        verbose_name=_('User'),
    )
    email = models.EmailField(verbose_name=_('Email'))
    syndic = models.ForeignKey(Syndic, on_delete=models.CASCADE, verbose_name=_('Syndic'), null=True, blank=True, related_name='syndic_coproprietaires')
    supersyndic = models.ForeignKey(SuperSyndic, on_delete=models.CASCADE, verbose_name=_('SuperSyndic'), null=True, blank=True, related_name='supersyndic_coproprietaires')
    residence = models.ManyToManyField(Residence, verbose_name=_('Residences'), blank=True, related_name='coproprietaire_residences')

    def __str__(self):
        return self.user.nom


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
    syndic = models.ForeignKey(Syndic, on_delete=models.CASCADE, verbose_name=_('Syndic'), null=True, blank=True)
    supersyndic = models.ForeignKey(SuperSyndic, on_delete=models.CASCADE, verbose_name=_('SuperSyndic'), null=True, blank=True)

    def __str__(self):
        return self.nom


# Apartment Information
class Appartement(models.Model):
    immeuble = models.ForeignKey(Residence, on_delete=models.CASCADE, verbose_name=_('Building'))
    numero = models.CharField(max_length=50, verbose_name=_('Number'))
    superficie = models.FloatField(verbose_name=_('Area'))
    proprietaire = models.ForeignKey(
        Coproprietaire, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('Owner')
    )
    occupation = models.CharField(
        max_length=50,
        choices=[
            ('Propriétaire', _('Owner')),
            ('Locataire', _('Tenant')),
            ('Vacant', _('Vacant')),
        ],
        verbose_name=_('Occupation'),
    )

    def __str__(self):
        return _("Apartment {number} - {building}").format(number=self.numero, building=self.immeuble.nom)


# Log modifications
class ModificationLog(models.Model):
    modele_modifie = models.CharField(max_length=255, verbose_name=_('Modified Model'))
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_('User'))
    action = models.CharField(max_length=50, verbose_name=_('Action'))
    date = models.DateTimeField(auto_now_add=True, verbose_name=_('Date'))
    details = models.TextField(verbose_name=_('Details'))

    def __str__(self):
        return _("{model} modified by {user} on {date}").format(
            model=self.modele_modifie, user=self.utilisateur.username, date=self.date
        )
