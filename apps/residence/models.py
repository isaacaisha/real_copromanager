# -*- encoding: utf-8 -*- apps/residence/forms.py

"""
Copyright (c) 2019 - present AppSeed.us
"""

from datetime import datetime
from django.conf import settings
from django.db import models
from django.utils.translation import gettext as _

from apps.authentication.models import CustomUser

from apps.syndic.models import Syndic

from apps.supersyndic.models import SuperSyndic

#from apps.coproprietaire.models import Coproprietaire


# Building Information
class Residence(models.Model):
    nom = models.CharField(max_length=255, verbose_name=_('Name'))
    adresse = models.TextField(verbose_name=_('Address'))

    # Optional fields: add blank=True and null=True
    nombre_appartements = models.IntegerField(verbose_name=_('Number of Apartments'), blank=True, null=True)
    superficie_totale = models.FloatField(verbose_name=_('Total Area'), blank=True, null=True)
    date_construction = models.DateField(verbose_name=_('Construction Date'), blank=True, null=True)
    nombre_etages = models.IntegerField(verbose_name=_('Number of Floors'), blank=True, null=True)
    zones_communes = models.TextField(verbose_name=_('Common Areas'), blank=True, null=True)
    date_dernier_controle = models.DateField(null=True, blank=True, verbose_name=_('Last Inspection Date'))
    type_chauffage = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('Heating Type'))
    
    syndic = models.ManyToManyField(Syndic, verbose_name=_('Syndic'), blank=True, related_name='syndic_residences')
    supersyndic = models.ManyToManyField(SuperSyndic, verbose_name=_('SuperSyndic'), blank=True, related_name='supersyndic_residences')
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_residences")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))

    extra_data = models.JSONField(null=True, blank=True, verbose_name=_('Extra Data'))

    
    def save(self, *args, **kwargs):
        # Ensure extra_data is a dictionary before modifying it
        if not isinstance(self.extra_data, dict) or self.extra_data is None:
            self.extra_data = {}

        # Ensure `created_at` is set and convert it to a proper string
        if self.created_at and isinstance(self.created_at, (datetime, str)):  
            formatted_created_at = self.created_at.strftime("%d %B %Y")
            self.extra_data["created_at"] = formatted_created_at  # ✅ Explicitly convert to string

        # Call the original save method
        super().save(*args, **kwargs)


    def __str__(self):
        return _("Building {name} ({address})").format(name=self.nom, address=self.adresse)

    def sync_to_odoo(self):
        """Sync this residence to Odoo"""
        import xmlrpc.client
        from django.conf import settings
        
        try:
            common = xmlrpc.client.ServerProxy(f"{settings.ODOO_URL}/xmlrpc/2/common")
            uid = common.authenticate(settings.ODOO_DB, settings.ODOO_USER, settings.ODOO_PASSWORD, {})
            
            models = xmlrpc.client.ServerProxy(f"{settings.ODOO_URL}/xmlrpc/2/object")
            models.execute_kw(
                settings.ODOO_DB, uid, settings.ODOO_PASSWORD,
                'residence.model', 'create', [{
                    'name': self.nom,
                    'address': self.adresse,
                    'syndic_ids': [s.id for s in self.syndic.all()],
                    'supersyndic_ids': [ss.id for ss in self.supersyndic.all()],
                    'created_by_id': self.created_by.id
                }]
            )
            return True
        except Exception as e:
            print(f"Odoo sync error: {e}")
            return False

# Apartment Information
class Appartement(models.Model):
    pass
#    immeuble = models.ForeignKey(Residence, on_delete=models.CASCADE, verbose_name=_('Building'))
#    numero = models.CharField(max_length=50, verbose_name=_('Number'))
#    superficie = models.FloatField(verbose_name=_('Area'))
#    proprietaire = models.ForeignKey(
#        Coproprietaire, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('Owner')
#    )
#    occupation = models.CharField(
#        max_length=50,
#        choices=[
#            ('Propriétaire', _('Owner')),
#            ('Locataire', _('Tenant')),
#            ('Vacant', _('Vacant')),
#        ],
#        verbose_name=_('Occupation'),
#    )
#
#    def __str__(self):
#        return _("Apartment {number} - {building}").format(number=self.numero, building=self.immeuble.nom)


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
