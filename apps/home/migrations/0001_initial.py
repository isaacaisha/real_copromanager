# Generated by Django 5.1.2 on 2024-10-26 04:30

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
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
                ('proprietaire', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='home.coproprietaire')),
                ('immeuble', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.immeuble')),
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
                ('license_base', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='syndic', to='home.licensebase')),
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
                ('license', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='syndic_license', to='home.license')),
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
                ('syndic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.syndic')),
            ],
        ),
        migrations.AddField(
            model_name='license',
            name='syndic',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='licenses', to='home.syndic'),
        ),
        migrations.AddField(
            model_name='immeuble',
            name='syndic',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.syndic'),
        ),
        migrations.AddField(
            model_name='coproprietaire',
            name='syndic',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.syndic'),
        ),
    ]