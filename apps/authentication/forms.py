# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm

from apps.authentication.models import CustomUser
from apps.home.models import License, SuperSyndic

# Import ReCaptchaField correctly
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox, ReCaptchaV3
from django.contrib.auth.forms import SetPasswordForm


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
        choices=[('Superadmin', 'Superadmin'), ('Syndic', 'Syndic'),
                 ('Coproprietaire', 'Coproprietaire'), ('Prestataire', 'Prestataire')],
        widget=forms.Select(
            attrs={
                "placeholder": "Role:",
                "class": "form-control"
            }
        ))
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Mot de passe",
                "class": "form-control"
            }
        ))
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Vérifier mot de passe",
                "class": "form-control"
            }
        ))
    
    # Use reCAPTCHA v3 for registration
    #captcha = ReCaptchaField(widget=ReCaptchaV3())

    class Meta:
        model = CustomUser
        fields = ('email', 'nom', 'prenom', 'role', 'password1', 'password2')


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
                "placeholder": "Mot de passe",
                "class": "form-control"
            }
        ))
    
    # Use reCAPTCHA v2 for login
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())


class CustomPasswordResetConfirmForm(SetPasswordForm):
    recaptcha = ReCaptchaField()

    def clean_recaptcha(self):
        # Here you can validate the ReCaptcha response if needed
        recaptcha_response = self.cleaned_data.get('recaptcha')

        # Custom validation logic for recaptcha (if required)
        if not recaptcha_response:
            raise forms.ValidationError("ReCAPTCHA validation failed. Please try again.")

        return recaptcha_response
    

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


class SuperSyndicForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['email', 'nom', 'prenom', 'password']
        widgets = {
            'password': forms.PasswordInput(),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.role = 'SuperSyndic'
        if commit:
            user.save()
            SuperSyndic.objects.create(user=user)  # Automatically link the user to SuperSyndic
        return user
