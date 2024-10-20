# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import CustomUser, License, LicenseBase


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Username",
                "class": "form-control",
                #"style": "font-size: 16px; color: #000;"
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
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Username",
                "class": "form-control"
            }
        ))
    nom = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Username nom",
                "class": "form-control"
            }
        ))
    role = forms.ChoiceField(
        choices=[('Superadmin', 'Superadmin'), ('Syndic', 'Syndic'), ('Coproprietaire', 'Coproprietaire'), ('Prestataire', 'Prestataire')],
        widget=forms.Select(
            attrs={
                "class": "form-control"
            }
        ))
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Email",
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
        fields = ('username', 'nom', 'role', 'email', 'password1', 'password2')


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
