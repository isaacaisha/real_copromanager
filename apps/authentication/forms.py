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


IS_ACTIVE_CHOICES = [
    (True, _("Active")),
    (False, _("Inactive")),
]
IS_SUPERUSER_CHOICES = [
    (True, _("Super User")),
    (False, _("Regular User")),
]
STATUS_CHOICES = [
    (True, _("Super Active")),
    (False, _("Active")),
]

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
    is_active = forms.ChoiceField(
        choices=IS_ACTIVE_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}
    ))
    is_superuser = forms.ChoiceField(
        choices=IS_SUPERUSER_CHOICES,
        required=False,
        initial=False,  # Default to False
        widget=forms.Select(attrs={"class": "form-control"}
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
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        initial=False,  # Default to False
        widget=forms.Select(attrs={"class": "form-control"}
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
            'email', 'nom', 'prenom', 'role', 'is_active', 'is_superuser', 
            'password1', 'password2',
            'residence', 'phone', 'status', 'commercial', 'address', 
            'city', 'country', 'postal_code', 'about_me'
        ]
    
    def __init__(self, *args, **kwargs):
        exclude_residence = kwargs.pop('exclude_residence', False)
        logged_in_user = kwargs.pop('logged_in_user', None)
        super().__init__(*args, **kwargs)

        # Only Superadmin can see the `is_active` field
        if logged_in_user and logged_in_user.role != 'Superadmin':
            self.fields.pop('is_active', None)
            self.fields.pop('is_superuser', None)
            self.fields.pop('status', None)

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

    def save(self, commit=True):
        user = super().save(commit=False)
        is_superuser = self.cleaned_data.get('is_superuser', False)

        # Ensure superuser permission is only set by a Superadmin
        logged_in_user = self.initial.get('logged_in_user')  # Ensure this is passed when initializing the form
        if logged_in_user and logged_in_user.role == 'Superadmin':
            user.is_superuser = is_superuser
            user.is_staff = is_superuser  # Superusers should also be staff
        else:
            # Do not force it to False if it's an update
            if not user.pk:  # Only reset for new users
                user.is_superuser = False
                user.is_staff = False

        if commit:
            user.save()
        return user

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')

        # Only validate residence if the field is present in the form
        if 'residence' in self.fields:
            residence = cleaned_data.get('residence')

            # Check if residence is required for the Coproprietaire & Prestataire role 
            if role in ['Coproprietaire', 'Prestataire'] and not residence:
            #if role == 'Coproprietaire' or 'Prestataire' and not residence:
                self.add_error('residence', _("Residence is required for User registration."))


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
        logged_in_user = kwargs.pop('logged_in_user', None)
        super().__init__(*args, **kwargs)

        # Only Superadmin can see the `is_active` field
        if logged_in_user and logged_in_user.role != 'Superadmin':
            self.fields.pop('is_active', None)
            self.fields.pop('is_superuser', None)
            self.fields.pop('status', None)

        # Remove the 'residence' field if it exists
        if 'residence' in self.fields:
            self.fields.pop('residence')

        # Only allow 'Superadmin' to select 'Syndic'
        if logged_in_user == 'Superadmin':
            self.fields['role'].choices = [
                ('Syndic', _('Syndic')),
            ]
        else:
            self.fields['role'].choices = [
                ('Syndic', _('Syndic')),
            ]

        #for field_name, field in self.fields.items():
        #    field.label = ""  # Remove labels


class SuperSyndicForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        
        fields = [
            'email', 'nom', 'prenom', 'is_active', 'is_superuser', 'phone', 'status', 
            'commercial', 'address', 'city', 'country', 
            'postal_code', 'about_me', 'password'
        ]
        widgets = {
            'email': forms.EmailInput(attrs={"placeholder": _("Email"), "class": "form-control"}),
            'nom': forms.TextInput(attrs={"placeholder": _("Last Name"), "class": "form-control"}),
            'prenom': forms.TextInput(attrs={"placeholder": _("First Name"), "class": "form-control"}),
            'is_active': forms.Select(attrs={"class": "form-control", "style": "border: none; background-color: transparent;"}),
            'is_superuser': forms.Select(attrs={"class": "form-control", "style": "border: none; background-color: transparent;"}),
            'phone': forms.TextInput(attrs={"placeholder": _("Phone"), "class": "form-control"}),
            'status': forms.Select(attrs={"class": "form-control", "style": "border: none; background-color: transparent;"}),
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
        # Extract the logged-in user's role from kwargs
        logged_in_user = kwargs.pop('logged_in_user', None)
        super().__init__(*args, **kwargs)

        # Remove help_text for is_superuser
        if 'is_superuser' in self.fields:
            self.fields['is_superuser'].help_text = ""

        # Only Superadmin can see the `is_active` field
        if logged_in_user and logged_in_user.role != 'Superadmin':
            self.fields.pop('is_active', None)
            self.fields.pop('is_superuser', None)
            self.fields.pop('status', None)

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