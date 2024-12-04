# -*- encoding: utf-8 -*- apps/dashboard/forms.py

"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import forms

from apps.dashboard.models import License

from django.utils.translation import gettext_lazy as _


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
        