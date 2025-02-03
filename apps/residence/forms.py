# -*- encoding: utf-8 -*- apps/residence/forms.py

"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import forms

from django.utils.translation import gettext as _

from .models import Residence

from apps.syndic.models import Syndic

from apps.supersyndic.models import SuperSyndic
        

class ResidenceForm(forms.ModelForm):
    """
    Form for creating or updating a Residence.
    """
    class Meta:
        model = Residence
        fields = [
            'nom',
            'adresse',
            'nombre_appartements',
            'superficie_totale',
            'date_construction',
            'nombre_etages',
            'zones_communes',
            'date_dernier_controle',
            'type_chauffage',
        ]
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Enter building name')}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'placeholder': _('Enter address'), 'rows': 3}),
            'nombre_appartements': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('Enter number of apartments')}),
            'superficie_totale': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('Enter total area (sqm)')}),
            'date_construction': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'nombre_etages': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('Enter number of floors')}),
            'zones_communes': forms.Textarea(attrs={'class': 'form-control', 'placeholder': _('List common areas (e.g., Hall, Garden, Parking)'), 'rows': 3}),
            'date_dernier_controle': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'type_chauffage': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Enter heating type')}),
        }
        labels = {
            'nom': _('Building Name'),
            'adresse': _('Address'),
            'nombre_appartements': _('Number of Apartments'),
            'superficie_totale': _('Total Area (sqm)'),
            'date_construction': _('Construction Date'),
            'nombre_etages': _('Number of Floors'),
            'zones_communes': _('Common Areas'),
            'date_dernier_controle': _('Last Inspection Date'),
            'type_chauffage': _('Heating Type'),
        }

    def save(self, user, target_user=None, commit=True):
        residence = super().save(commit=False)

        # Automatically set the 'created_by' field to the logged-in user
        residence.created_by = user

        # Handle syndic or supersyndic associations
        try:
            if target_user:  # For residence creation with a target user
                if target_user.role in ['Syndic', 'SuperSyndic']:
                    syndic_instance = Syndic.objects.filter(user=target_user).first()
                    supersyndic_instance = SuperSyndic.objects.filter(user=target_user).first()

                    if syndic_instance:
                        residence.save()  # Save residence first before modifying ManyToMany fields
                        residence.syndic.add(syndic_instance)  # Use `.add()` for ManyToManyField
                    if supersyndic_instance:
                        residence.save()
                        residence.supersyndic.add(supersyndic_instance)
                else:
                    raise ValueError(_("Target user must be a Syndic or SuperSyndic."))
            else:  # For updates or creation without a target user
                if user.role in ['Syndic', 'SuperSyndic']:
                    syndic_instance = Syndic.objects.filter(user=user).first()
                    supersyndic_instance = SuperSyndic.objects.filter(user=user).first()

                    if syndic_instance:
                        residence.save()
                        residence.syndic.add(syndic_instance)
                    if supersyndic_instance:
                        residence.save()
                        residence.supersyndic.add(supersyndic_instance)
                elif user.role == 'Superadmin':
                    # Allow Superadmin to update without specific syndic assignment
                    pass
                else:
                    raise ValueError(_("Only Syndics or SuperSyndics can create or update residences."))
        except Syndic.DoesNotExist:
            raise ValueError(_("No Syndic instance found for the target user."))
        except SuperSyndic.DoesNotExist:
            raise ValueError(_("No SuperSyndic instance found for the target user."))

        if commit:
            residence.save()
        return residence
    