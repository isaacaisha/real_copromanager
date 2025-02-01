# -*- encoding: utf-8 -*- apps/authentication/forms.py

"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import forms
from django.utils.translation import gettext as _

from apps.authentication.models import CustomUser

from apps.supersyndic.models import SuperSyndic


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
            