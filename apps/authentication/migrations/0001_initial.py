# Generated by Django 5.1.2 on 2024-10-26 01:52

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Immeuble',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=255)),
                ('adresse', models.TextField()),
                ('nombre_appartements', models.IntegerField()),
                ('superficie_totale', models.FloatField()),
                ('date_construction', models.DateField()),
                ('nombre_etages', models.IntegerField()),
                ('zones_communes', models.TextField()),
                ('date_dernier_controle', models.DateField(blank=True, null=True)),
                ('type_chauffage', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='LicenseBase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=255, unique=True)),
                ('fonctionnalites', models.JSONField()),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(max_length=254, null=True, unique=True)),
                ('nom', models.CharField(max_length=255)),
                ('prenom', models.CharField(max_length=255)),
                ('role', models.CharField(choices=[('Superadmin', 'Superadmin'), ('Syndic', 'Syndic'), ('Coproprietaire', 'Coproprietaire'), ('Prestataire', 'Prestataire')], default='Syndic', max_length=50)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Coproprietaire',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254)),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='coproprietaire_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Appartement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero', models.CharField(max_length=50)),
                ('superficie', models.FloatField()),
                ('occupation', models.CharField(choices=[('Propriétaire', 'Propriétaire'), ('Locataire', 'Locataire'), ('Vacant', 'Vacant')], max_length=50)),
                ('proprietaire', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='authentication.coproprietaire')),
                ('immeuble', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='authentication.immeuble')),
            ],
        ),
        migrations.CreateModel(
            name='License',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_debut', models.DateField(blank=True, null=True)),
                ('date_fin', models.DateField(blank=True, null=True)),
                ('fonctionnalites_personnalisees', models.JSONField(blank=True, null=True)),
                ('est_personnalise', models.BooleanField(default=True)),
                ('license_base', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='syndic', to='authentication.licensebase')),
            ],
        ),
        migrations.CreateModel(
            name='ModificationLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('modele_modifie', models.CharField(max_length=255)),
                ('action', models.CharField(max_length=50)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('details', models.TextField()),
                ('utilisateur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Superadmin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='superadmin_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Syndic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254)),
                ('license', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='syndic_license', to='authentication.license')),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='syndic_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Prestataire',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254)),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='prestataire_profile', to=settings.AUTH_USER_MODEL)),
                ('syndic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='authentication.syndic')),
            ],
        ),
        migrations.AddField(
            model_name='license',
            name='syndic',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='licenses', to='authentication.syndic'),
        ),
        migrations.AddField(
            model_name='immeuble',
            name='syndic',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='authentication.syndic'),
        ),
        migrations.AddField(
            model_name='coproprietaire',
            name='syndic',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='authentication.syndic'),
        ),
    ]
