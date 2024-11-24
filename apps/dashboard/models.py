## -*- encoding: utf-8 -*-
#"""
#Copyright (c) 2019 - present AppSeed.us
#"""
#
#from django.conf import settings
#from django.db import models
#
## Create your models here.
#
## -*- encoding: utf-8 -*-
#"""
#Copyright (c) 2019 - present AppSeed.us
#"""
## home/models.py
## Create your models here.
#
## Superadmin Model
#class Superadmin(models.Model):
#    user = models.OneToOneField(settings.AUTH_USER_MODEL,
#                                on_delete=models.CASCADE,
#                                related_name='superadmin_profile')
#    
#    def __str__(self):
#        return f"Superadmin: {self.user.email}"
#
#
## Licence Base
#class LicenseBase(models.Model):
#    nom = models.CharField(max_length=255, unique=True)
#    # Contient les fonctionnalités disponibles dans cette licence de base
#    fonctionnalites = models.JSONField()
#    date_creation = models.DateTimeField(auto_now_add=True)
#    
#    def __str__(self):
#        return self.nom
#    
#
## Custom License for Syndic
#class License(models.Model):
#    syndic = models.ForeignKey(
#        'Syndic', on_delete=models.CASCADE, related_name='syndic_licenses', null=True, blank=True
#    )
#    super_syndic = models.ForeignKey(
#        'SuperSyndic', on_delete=models.CASCADE, related_name='super_syndic_licenses', null=True, blank=True
#    )
#    license_base = models.ForeignKey(
#        LicenseBase, on_delete=models.SET_NULL, null=True, blank=True, related_name='licenses'
#    )
#    date_debut = models.DateField(null=True, blank=True)
#    date_fin = models.DateField(null=True, blank=True)
#    fonctionnalites_personnalisees = models.JSONField(null=True, blank=True)
#    est_personnalise = models.BooleanField(default=True)
#
#    def get_fonctionnalites(self):
#        if self.est_personnalise and self.fonctionnalites_personnalisees:
#            return self.fonctionnalites_personnalisees
#        elif self.license_base:
#            return self.license_base.fonctionnalites
#        return []
#
#    def __str__(self):
#        role = self.syndic or self.super_syndic
#        return f"License for {role.nom} (from {self.date_debut} to {self.date_fin})"
#
#
#class SuperSyndic(models.Model):
#    nom = models.CharField(max_length=255)
#    user = models.OneToOneField(settings.AUTH_USER_MODEL,
#                                on_delete=models.CASCADE,
#                                related_name='super_syndic_profile',
#                                null=True, blank=True)
#    email = models.EmailField()
#
#    def __str__(self):
#        return self.nom
#
#
## Syndic Information
#class Syndic(models.Model):
#    nom = models.CharField(max_length=255)
#    user = models.OneToOneField(settings.AUTH_USER_MODEL,
#                                on_delete=models.CASCADE,
#                                related_name='syndic_profile',
#                                null=True, blank=True)
#    email = models.EmailField()
#
#    def __str__(self):
#        return self.nom
#
#
## Co-owner Information
#class Coproprietaire(models.Model):
#    nom = models.CharField(max_length=255)
#    user = models.OneToOneField(settings.AUTH_USER_MODEL,
#                                on_delete=models.CASCADE,
#                                related_name='coproprietaire_profile',
#                                null=True, blank=True)
#    email = models.EmailField()
#    syndic = models.ForeignKey(Syndic, on_delete=models.CASCADE)
#
#    def __str__(self):
#        return self.nom
#
#
## Provider Information
#class Prestataire(models.Model):
#    nom = models.CharField(max_length=255)
#    user = models.OneToOneField(settings.AUTH_USER_MODEL,
#                                on_delete=models.CASCADE,
#                                related_name='prestataire_profile',
#                                null=True, blank=True)
#    email = models.EmailField()
#    syndic = models.ForeignKey(Syndic, on_delete=models.CASCADE)
#
#    def __str__(self):
#        return self.nom
#
#
## Building Information
#class Immeuble(models.Model):
#    nom = models.CharField(max_length=255)
#    adresse = models.TextField()
#    syndic = models.ForeignKey(Syndic, on_delete=models.CASCADE)
#    nombre_appartements = models.IntegerField()
#    superficie_totale = models.FloatField()
#    date_construction = models.DateField()
#    nombre_etages = models.IntegerField()
#    zones_communes = models.TextField()  # Example: "Hall, Garden, Parking"
#
#    date_dernier_controle = models.DateField(null=True, blank=True)
#    type_chauffage = models.CharField(max_length=255, null=True, blank=True)
#
#    def __str__(self):
#        return f"{self.nom} ({self.adresse})"
#
#
## Apartment Information
#class Appartement(models.Model):
#    immeuble = models.ForeignKey(Immeuble, on_delete=models.CASCADE)
#    numero = models.CharField(max_length=50)
#    superficie = models.FloatField()
#    proprietaire = models.ForeignKey(Coproprietaire, on_delete=models.SET_NULL, null=True, blank=True)
#    occupation = models.CharField(max_length=50, choices=[('Propriétaire', 'Propriétaire'), ('Locataire', 'Locataire'), ('Vacant', 'Vacant')])
#
#    def __str__(self):
#        return f"Apartment {self.numero} - {self.immeuble.nom}"
#
#
## Log modifications
#class ModificationLog(models.Model):
#    modele_modifie = models.CharField(max_length=255)
#    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#    action = models.CharField(max_length=50)
#    date = models.DateTimeField(auto_now_add=True)
#    details = models.TextField()
#
#    def __str__(self):
#        return f"{self.modele_modifie} modified by {self.utilisateur.username} on {self.date}"
#