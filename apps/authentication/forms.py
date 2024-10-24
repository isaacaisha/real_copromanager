# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, License, LicenseBase


class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Email",
                "class": "form-control",
            }
        ))
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": "form-control"
            }
        ))


class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Email",
                "class": "form-control"
            }
        ))
    nom = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Nom",
                "class": "form-control"
            }
        ))
    prenom = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Prenom",
                "class": "form-control"
            }
        ))
    role = forms.ChoiceField(
        choices=[('Superadmin', 'Superadmin'), ('Syndic', 'Syndic'), ('Coproprietaire', 'Coproprietaire'), ('Prestataire', 'Prestataire')],
        widget=forms.Select(
            attrs={
                "placeholder": "Role:",
                "class": "form-control"
            }
        ))
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": "form-control"
            }
        ))
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password check",
                "class": "form-control"
            }
        ))

    class Meta:
        model = CustomUser
        fields = ('email', 'nom', 'prenom', 'role', 'password1', 'password2')


class LicenseForm(forms.ModelForm):
    class Meta:
        model = License
        fields = ['date_debut', 'date_fin', 'fonctionnalites_personnalisees', 'est_personnalise'] # 'license_base', 
        
        widgets = {
            #'license_base': forms.Select(attrs={"class": "form-control"}),
            'date_debut': forms.DateInput(attrs={"class": "form-control", "type": "date", "placeholder": "Start Date"}),
            'date_fin': forms.DateInput(attrs={"class": "form-control", "type": "date", "placeholder": "End Date"}),
            'fonctionnalites_personnalisees': forms.DateInput(attrs={"class": "form-control", "placeholder": "Customized Features (optional)"}),
            'est_personnalise': forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    #def __init__(self, *args, **kwargs):
    #    super().__init__(*args, **kwargs)
    #    # Ensure the license_base queryset is active licenses
    #    self.fields['license_base'].queryset = LicenseBase.objects.all()
