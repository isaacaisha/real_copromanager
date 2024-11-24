## -*- encoding: utf-8 -*-
#"""
#Copyright (c) 2019 - present AppSeed.us
#"""
#
#from django import forms
#
#from apps.dashboard.models import License
#
#
#class LicenseForm(forms.ModelForm):
#    class Meta:
#        model = License
#        fields = ['date_debut', 'date_fin', 'fonctionnalites_personnalisees', 'est_personnalise'] # 'license_base', 
#        
#        widgets = {
#            #'license_base': forms.Select(attrs={"class": "form-control"}),
#            'date_debut': forms.DateInput(attrs={"class": "form-control", "type": "date", "placeholder": "Start Date"}),
#            'date_fin': forms.DateInput(attrs={"class": "form-control", "type": "date", "placeholder": "End Date"}),
#            'fonctionnalites_personnalisees': forms.DateInput(attrs={"class": "form-control", "placeholder": "Customized Features (optional)"}),
#            'est_personnalise': forms.CheckboxInput(attrs={"class": "form-check-input"}),
#        }
#
#    #def __init__(self, *args, **kwargs):
#    #    super().__init__(*args, **kwargs)
#    #    # Ensure the license_base queryset is active licenses
#    #    self.fields['license_base'].queryset = LicenseBase.objects.all()
#        