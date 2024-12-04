# -*- encoding: utf-8 -*- apps/authentication/forms.py

"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _

from apps.authentication.models import CustomUser
from apps.dashboard.models import License, SuperSyndic

# Import ReCaptchaField correctly
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox, ReCaptchaV3
from django.contrib.auth.forms import SetPasswordForm


class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "placeholder": _("Email"),
                "class": "form-control"
            }
        ))
    nom = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": _("last name"),
                "class": "form-control"
            }
        ))
    prenom = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": _("first name"),
                "class": "form-control"
            }
        ))
    role = forms.ChoiceField(
        choices=[('Syndic', _('Syndic')), 
                 ('Coproprietaire', _('Coproprietaire')), 
                 ('Prestataire', _('Prestataire'))
                 ],
        widget=forms.Select(
            attrs={
                "placeholder": _("Role:"),
                "class": "form-control"
            }
        ))
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": _("Password"),
                "class": "form-control"
            }
        ))
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": _("Confirm Password"),
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
                "placeholder": _("Email"),
                "class": "form-control",
            }
        ))
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": _("Password"),
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
            raise forms.ValidationError(_("ReCAPTCHA validation failed. Please try again."))

        return recaptcha_response


class SuperSyndicForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['email', 'nom', 'prenom', 'password']
        widgets = {
            'password': forms.PasswordInput(attrs={"placeholder": _("Password")}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.role = 'SuperSyndic'
        if commit:
            user.save()
            SuperSyndic.objects.create(user=user)  # Automatically link the user to SuperSyndic
        return user
