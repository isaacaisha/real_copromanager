# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
# models.py
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


# Custom User Model with roles
class CustomUser(AbstractUser):
    ROLES = (
        ('Superadmin', 'Superadmin'),
        ('Syndic', 'Syndic'),
        ('Coproprietaire', 'Coproprietaire'),
        ('Prestataire', 'Prestataire'),
    )
    nom = models.CharField(max_length=255)
    role = models.CharField(max_length=50, choices=ROLES, default='Syndic')
    email = models.EmailField(unique=True)  # Ensure email is unique

    # Adding related_name attributes to avoid conflicts
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',  # Avoids conflict with auth.User
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',  # Avoids conflict with auth.User
        blank=True
    )

    def __str__(self):
        return f"{self.nom} ({self.username})"


# Superadmin Model
class Superadmin(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='superadmin_profile')
    
    def __str__(self):
        return f"Superadmin: {self.user.username}"


# Licence Base
class LicenseBase(models.Model):
    nom = models.CharField(max_length=255, unique=True)
    fonctionnalites = models.JSONField()  # Contient les fonctionnalités disponibles dans cette licence de base
    date_creation = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nom
    

# Custom License for Syndic
class License(models.Model):
    syndic = models.ForeignKey('Syndic', on_delete=models.CASCADE, related_name='licenses')
    license_base = models.ForeignKey(LicenseBase, on_delete=models.SET_NULL, null=True, blank=True, related_name='syndic')
    date_debut = models.DateField(null=True, blank=True)
    date_fin = models.DateField(null=True, blank=True)
    fonctionnalites_personnalisees = models.JSONField(null=True, blank=True)  # Custom features for this license
    est_personnalise = models.BooleanField(default=True)

    def get_fonctionnalites(self):
        if self.est_personnalise and self.fonctionnalites_personnalisees:
            return self.fonctionnalites_personnalisees
        elif self.license_base:
            return self.license_base.fonctionnalites
        return []

    def __str__(self):
        return f"Licence for {self.syndic.nom} (from {self.date_debut} to {self.date_fin})"


# Syndic Information
class Syndic(models.Model):
    nom = models.CharField(max_length=255)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='syndic_profile', null=True, blank=True)
    email = models.EmailField()
    license = models.OneToOneField(License, on_delete=models.CASCADE, null=True, related_name='syndic_license')

    def __str__(self):
        return self.nom


# Co-owner Information
class Coproprietaire(models.Model):
    nom = models.CharField(max_length=255)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='coproprietaire_profile', null=True, blank=True)
    email = models.EmailField()
    syndic = models.ForeignKey(Syndic, on_delete=models.CASCADE)

    def __str__(self):
        return self.nom


# Provider Information
class Prestataire(models.Model):
    nom = models.CharField(max_length=255)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='prestataire_profile', null=True, blank=True)
    email = models.EmailField()
    syndic = models.ForeignKey(Syndic, on_delete=models.CASCADE)

    def __str__(self):
        return self.nom


# Building Information
class Immeuble(models.Model):
    nom = models.CharField(max_length=255)
    adresse = models.TextField()
    syndic = models.ForeignKey(Syndic, on_delete=models.CASCADE)
    nombre_appartements = models.IntegerField()
    superficie_totale = models.FloatField()
    date_construction = models.DateField()
    nombre_etages = models.IntegerField()
    zones_communes = models.TextField()  # Example: "Hall, Garden, Parking"

    date_dernier_controle = models.DateField(null=True, blank=True)
    type_chauffage = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.nom} ({self.adresse})"


# Apartment Information
class Appartement(models.Model):
    immeuble = models.ForeignKey(Immeuble, on_delete=models.CASCADE)
    numero = models.CharField(max_length=50)
    superficie = models.FloatField()
    proprietaire = models.ForeignKey(Coproprietaire, on_delete=models.SET_NULL, null=True, blank=True)
    occupation = models.CharField(max_length=50, choices=[('Propriétaire', 'Propriétaire'), ('Locataire', 'Locataire'), ('Vacant', 'Vacant')])

    def __str__(self):
        return f"Apartment {self.numero} - {self.immeuble.nom}"


# Log modifications
class ModificationLog(models.Model):
    modele_modifie = models.CharField(max_length=255)
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    action = models.CharField(max_length=50)
    date = models.DateTimeField(auto_now_add=True)
    details = models.TextField()

    def __str__(self):
        return f"{self.modele_modifie} modified by {self.utilisateur.username} on {self.date}"
