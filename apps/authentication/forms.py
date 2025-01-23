# -*- encoding: utf-8 -*- apps/authentication/forms.py

"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext as _

from apps.authentication.models import CustomUser
from apps.dashboard.models import SuperSyndic, Residence

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
    #role = forms.CharField(
    #    choices=[
    #            ('Syndic', _('Syndic')),
    #            ('Coproprietaire', _('Coproprietaire')),
    #            ('Prestataire', _('Prestataire')),
    #        ],
    #    #widget=forms.HiddenInput()  # Make it hidden
    #    widget=forms.Select(
    #        attrs={
    #            "readonly": True,  # Make the field read-only
    #            "placeholder": _("Role:"),
    #            "class": "form-control"
    #        }
    #    ))
    role = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "readonly": True,  # Make the field read-only
                "placeholder": _("Role"),
                "class": "form-control",
                "style": "background-color: transparent;" 
            }
        ))
    residence = forms.ModelChoiceField(
        queryset=Residence.objects.none(),  # Default to an empty queryset
        required=False,  # Default to not required
        widget=forms.Select(
            attrs={
                "placeholder": _("Residences"),
                "class": "form-control"
            }
        ))
    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": _("Phone Number"),
                "class": "form-control"
            }
        ))
    status = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": _("Status (e.g., Active/Inactive)"),
                "class": "form-control"
            }
        ))
    commercial = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": _("Commercial Information"),
                "class": "form-control"
            }
        ))
    address = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "placeholder": _("Address"),
                "class": "form-control",
                "rows": 2
            }
        ))
    city = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": _("City"),
                "class": "form-control"
            }
        ))
    country = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": _("Country"),
                "class": "form-control"
            }
        ))
    postal_code = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": _("Postal Code"),
                "class": "form-control"
            }
        ))
    about_me = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "placeholder": _("About Me"),
                "class": "form-control",
                "rows": 3
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
        fields = [
            'email', 'nom', 'prenom', 'role', 'residence', 
            'phone', 'status', 'commercial', 'address', 
            'city', 'country', 'postal_code', 'about_me', 
            'password1', 'password2'
        ]
    
    def __init__(self, *args, **kwargs):
        exclude_residence = kwargs.pop('exclude_residence', False)
        logged_in_user = kwargs.pop('logged_in_user', None)
        super().__init__(*args, **kwargs)

        # Optionally exclude the residence field
        if exclude_residence:
            self.fields.pop('residence', None)
        else:
            # Filter residences based on logged-in user's role only if the field is present
            if logged_in_user:
                if logged_in_user.role == 'Syndic':
                    self.fields['residence'].queryset = Residence.objects.filter(syndic__user=logged_in_user)
                elif logged_in_user.role == 'SuperSyndic':
                    self.fields['residence'].queryset = Residence.objects.filter(supersyndic__user=logged_in_user)

        # Restrict the initial role from provided data
        if 'role' in self.initial:
            self.fields['role'].initial = self.initial['role']

        # Remove field labels
        for field_name, field in self.fields.items():
            field.label = ""  # Removing labels as per requirement

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
    
        # Only validate residence if the field is present in the form
        if 'residence' in self.fields:
            residence = cleaned_data.get('residence')

            # Check if residence is required for the Coproprietaire role
            if role == 'Coproprietaire' and not residence:
                self.add_error('residence', _("Residence is required for Coproprietaire registration."))


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


class SyndicForm(SignUpForm):
    class Meta(SignUpForm.Meta):
        model = CustomUser
        fields = SignUpForm.Meta.fields

    def __init__(self, *args, **kwargs):
        # Extract the logged-in user's role from kwargs
        logged_in_user_role = kwargs.pop('logged_in_user_role', None)
        super().__init__(*args, **kwargs)

        # Remove the 'residence' field if it exists
        if 'residence' in self.fields:
            self.fields.pop('residence')

        # Only allow 'Superadmin' to select 'Syndic'
        if logged_in_user_role == 'Superadmin':
            self.fields['role'].choices = [
                ('Syndic', _('Syndic')),
            ]
        else:
            self.fields['role'].choices = [
                ('Syndic', _('Syndic')),
            ]

        for field_name, field in self.fields.items():
            field.label = ""  # Remove labels


class SuperSyndicForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'email', 'nom', 'prenom', 'phone', 'status', 
            'commercial', 'address', 'city', 'country', 
            'postal_code', 'about_me', 'password'
        ]
        widgets = {
            'email': forms.EmailInput(attrs={"placeholder": _("Email"), "class": "form-control"}),
            'nom': forms.TextInput(attrs={"placeholder": _("Last Name"), "class": "form-control"}),
            'prenom': forms.TextInput(attrs={"placeholder": _("First Name"), "class": "form-control"}),
            'phone': forms.TextInput(attrs={"placeholder": _("Phone"), "class": "form-control"}),
            'status': forms.TextInput(attrs={"placeholder": _("Status (Active/Inactive)"), "class": "form-control"}),
            'commercial': forms.TextInput(attrs={"placeholder": _("Commercial Info"), "class": "form-control"}),
            'address': forms.Textarea(attrs={"placeholder": _("Address"), "class": "form-control", "rows": 2}),
            'city': forms.TextInput(attrs={"placeholder": _("City"), "class": "form-control"}),
            'country': forms.TextInput(attrs={"placeholder": _("Country"), "class": "form-control"}),
            'postal_code': forms.TextInput(attrs={"placeholder": _("Postal Code"), "class": "form-control"}),
            'about_me': forms.Textarea(attrs={"placeholder": _("About Me"), "class": "form-control", "rows": 3}),
            'password': forms.PasswordInput(attrs={"placeholder": _("Password"), "class": "form-control"}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])  # Securely set the password
        user.role = 'SuperSyndic'  # Assign the SuperSyndic role
        if commit:
            user.save()
            # Automatically create and link the user to a SuperSyndic instance
            SuperSyndic.objects.create(user=user)
        return user

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.label = ""  # Remove labels


class CustomPasswordResetConfirmForm(SetPasswordForm):
    recaptcha = ReCaptchaField()

    def clean_recaptcha(self):
        # Here you can validate the ReCaptcha response if needed
        recaptcha_response = self.cleaned_data.get('recaptcha')

        # Custom validation logic for recaptcha (if required)
        if not recaptcha_response:
            raise forms.ValidationError(_("ReCAPTCHA validation failed. Please try again."))

        return recaptcha_response