# -*- encoding: utf-8 -*- apps/dashboard/forms.py

"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import forms

from apps.dashboard.models import License, Residence, SuperSyndic, Syndic

from django.utils.translation import gettext as _


class LicenseForm(forms.ModelForm):
    class Meta:
        model = License
        fields = ['date_debut', 'date_fin', 'fonctionnalites_personnalisees', 'est_personnalise'] # 'license_base', 
        
        # Add labels and error_messages
        labels = {
            'date_debut': _('Start Date'),
            'date_fin': _('End Date'),
            'fonctionnalites_personnalisees': _('Customized Features'),
            'est_personnalise': _('Is Customized'),
        }

        error_messages = {
            'date_debut': {
                'required': _('Start date is required.'),
            },
            'date_fin': {
                'required': _('End date is required.'),
            },
        }

        widgets = {
            # 'license_base': forms.Select(attrs={"class": "form-control"}),
            'date_debut': forms.DateInput(
                attrs={
                    "class": "form-control", 
                    "type": "date", 
                    "placeholder": _("Start Date")
                }
            ),
            'date_fin': forms.DateInput(
                attrs={
                    "class": "form-control", 
                    "type": "date", 
                    "placeholder": _("End Date")
                }
            ),
            'fonctionnalites_personnalisees': forms.TextInput(
                attrs={
                    "class": "form-control", 
                    "placeholder": _("Customized Features (optional)")
                }
            ),
            'est_personnalise': forms.CheckboxInput(
                attrs={
                    "class": "form-check-input"
                }
            ),
        }

    #def __init__(self, *args, **kwargs):
    #    super().__init__(*args, **kwargs)
    #    # Ensure the license_base queryset is active licenses
    #    self.fields['license_base'].queryset = LicenseBase.objects.all()
        

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
        
    def save(self, user, commit=True):
        residence = super().save(commit=False)
        try:
            if user.role == 'Syndic':
                residence.syndic = Syndic.objects.get(user=user)
            elif user.role == 'SuperSyndic':
                residence.supersyndic = SuperSyndic.objects.get(user=user)
            elif user.role == 'Superadmin':
                residence.syndic = Syndic.objects.get(user=user)
                #residence.supersyndic = SuperSyndic.objects.get(user=user)
            else:
                raise ValueError("Invalid user role or missing profile.")
        except Syndic.DoesNotExist:
            raise ValueError("Syndic not found for the user.")
        except SuperSyndic.DoesNotExist:
            raise ValueError("SuperSyndic not found for the user.")
    
        if commit:
            residence.save()
        return residence
