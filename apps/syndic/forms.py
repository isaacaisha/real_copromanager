# -*- encoding: utf-8 -*- apps/syndic/forms.py

"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.utils.translation import gettext as _

from apps.authentication.forms import SignUpForm
from apps.authentication.models import CustomUser


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
            