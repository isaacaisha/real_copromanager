# -*- encoding: utf-8 -*- apps/authentication/models.py

"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager

from django.utils.translation import gettext as _

# Create your models here.

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user with an email and password."""
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser with an email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)

# Custom User Model with roles
class CustomUser(AbstractUser):
    ROLES = (
        ('Superadmin', _('Superadmin')),
        ('Syndic', _('Syndic')),
        ('Coproprietaire', _('Coproprietaire')),
        ('Prestataire', _('Prestataire')),
        ('SuperSyndic', _('SuperSyndic')),
    )

    # Remove username field
    username = None
    
    email = models.EmailField(_('email address'), unique=True, null=True)  # Ensure email is unique
    nom = models.CharField(_('last name'), max_length=255)
    prenom = models.CharField(_('first name'), max_length=255)
    role = models.CharField(_('role'), max_length=50, choices=ROLES, default='Syndic')

    # Additional fields
    phone = models.CharField(_('phone'), max_length=20, null=True, blank=True)
    status = models.CharField(_('status'), max_length=100, null=True, blank=True)
    commercial = models.CharField(_('commercial'), max_length=100, null=True, blank=True)
    address = models.TextField(_('address'), null=True, blank=True)
    city = models.CharField(_('city'), max_length=100, null=True, blank=True)
    country = models.CharField(_('country'), max_length=100, null=True, blank=True)
    postal_code = models.CharField(_('postal code'), max_length=20, null=True, blank=True)
    about_me = models.TextField(_('about me'), null=True, blank=True)

    # Set email as the username field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nom', 'prenom', 'role']  # do not use verbose translations here

    # Link the custom manager to the User model
    objects = UserManager()

    def __str__(self):
        return f"{self.email} ({self.nom} {self.prenom} ({self.role})"
    