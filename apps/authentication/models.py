# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
# models.py
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager

# Create your models here.

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user with an email and password."""
        if not email:
            raise ValueError('The Email field must be set')
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
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

# Custom User Model with roles
class CustomUser(AbstractUser):
    ROLES = (
        ('Superadmin', 'Superadmin'),
        ('Syndic', 'Syndic'),
        ('Coproprietaire', 'Coproprietaire'),
        ('Prestataire', 'Prestataire'),
    )

    # Remove username field
    username = None
    
    email = models.EmailField(unique=True, null=True)  # Ensure email is unique
    nom = models.CharField(max_length=255)
    prenom = models.CharField(max_length=255)
    role = models.CharField(max_length=50, choices=ROLES, default='Syndic')

    # Set email as the username field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nom', 'prenom', 'role']  # Fields required besides email

    # Link the custom manager to the User model
    objects = UserManager()

    def __str__(self):
        return f"{self.email} ({self.nom} {self.prenom} ({self.role})"
    