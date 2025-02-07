# -*- encoding: utf-8 -*- apps/import_data/views.py

import pandas as pd

from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import gettext as _
from django.contrib import messages
from django.utils import timezone

from apps.authentication.models import CustomUser

from apps.import_data.utils_import_data import parse_excel_date, to_int, to_float

from apps.residence.models import Residence

from apps.syndic.models import Syndic

from apps.supersyndic.models import SuperSyndic

from .forms import ImportExcelForm


@login_required
@user_passes_test(lambda u: u.is_active and u.role in ['Superadmin', 'Syndic', 'SuperSyndic'])
def import_residences(request, user_id=None):
    """
    If the logged-in user is Superadmin and a user_id is provided in the URL,
    then use that user as the target for import (i.e. perform the import as if they were that Syndic or SuperSyndic).
    Otherwise, use the current user.
    """
    # Use the URL parameter user_id when the logged-in user is Superadmin.
    if request.user.role == "Superadmin":
        target_profile = get_object_or_404(CustomUser, id=user_id)
    else:
        target_profile = request.user

    if request.method == "POST":
        form = ImportExcelForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                df = pd.read_excel(request.FILES['file'])

                report = {'success': 0, 'errors': [], 'total': len(df)}
                known_columns = {
                    'Nom',
                    'Adresse',
                    'Nombre Appartements',
                    'Superficie Totale',
                    'Date Construction',
                    'Nombre Etages',
                    'Zones Communes',
                    'Date Dernier Contrôle',
                    'Type Chauffage',
                    'Syndics',
                    'SuperSyndics'
                }

                # Only require "Nom" and "Adresse"
                def validate_required(field_name, value):
                    if pd.isnull(value) or str(value).strip() == "":
                        raise ValueError(f"Missing required field: {field_name}")
                    return str(value).strip()
                

                def get_column_value(row, column_name):
                    for key, value in row.items():
                        if key.lower() == column_name.lower():
                            return value
                    return None

                last_residence = None  # To store the last processed Residence

                for index, row in df.iterrows():
                    try:
                        # Read and standardize the required fields:
                        nom = validate_required('Nom', get_column_value(row, 'Nom')).strip().title() # Convert to title case
                        adresse = validate_required('Adresse', get_column_value(row, 'Adresse')).strip().title() # Convert to title case
                        # Date fields are optional
                        date_construction = parse_excel_date(row.get('Date Construction'))
                        date_dernier = parse_excel_date(row.get('Date Dernier Contrôle'))

                        # Collect extra data: any column not in known_columns.
                        extra_data = {}
                        for col in df.columns:
                            if col not in known_columns:
                                value = row.get(col)
                                if isinstance(value, pd.Timestamp):
                                    value = value.strftime("%d-%m-%Y")  # Format as 'DD-MM-YYYY'
                                extra_data[col] = value

                        # Update or create Residence using 'nom' and 'adresse' as unique keys.
                        residence, created = Residence.objects.update_or_create(
                            nom=nom,
                            adresse=adresse,
                            defaults={
                                "nombre_appartements": to_int(row.get('Nombre Appartements'), 0),
                                "superficie_totale": to_float(row.get('Superficie Totale'), 0.0),
                                "date_construction": date_construction,
                                "nombre_etages": to_int(row.get('Nombre Etages'), 0),
                                "zones_communes": row.get('Zones Communes') or "",
                                "date_dernier_controle": date_dernier,
                                "type_chauffage": row.get('Type Chauffage') or "",
                                "extra_data": extra_data,
                                "created_by": target_profile
                            }
                        )

                        last_residence = residence

                        # Auto-assign relationships based on target_profile's role.
                        if target_profile.role == 'Syndic':
                            try:
                                syndic = Syndic.objects.get(user=target_profile)
                                residence.syndic.add(syndic)
                            except Syndic.DoesNotExist:
                                messages.warning(request, f"No Syndic record found for {target_profile.nom}")
                        elif target_profile.role == 'SuperSyndic':
                            try:
                                supersyndic = SuperSyndic.objects.get(user=target_profile)
                                residence.supersyndic.add(supersyndic)
                            except SuperSyndic.DoesNotExist:
                                messages.warning(request, f"No SuperSyndic record found for {target_profile.nom}")

                        # Process additional relationships (if provided in Excel)
                        syndic_field = row.get('Syndics', '')
                        if syndic_field and not pd.isnull(syndic_field):
                            for name in syndic_field.split(','):
                                name = name.strip()
                                if name:
                                    syndic, _ = Syndic.objects.get_or_create(nom=name)
                                    residence.syndic.add(syndic)

                        supersyndic_field = row.get('SuperSyndics', '')
                        if supersyndic_field and not pd.isnull(supersyndic_field):
                            for name in supersyndic_field.split(','):
                                name = name.strip()
                                if name:
                                    supersyndic, _ = SuperSyndic.objects.get_or_create(nom=name)
                                    residence.supersyndic.add(supersyndic)

                        # Sync with Odoo (if implemented)
                        if residence.sync_to_odoo():
                            report['success'] += 1
                        else:
                            report['errors'].append(f"Row {index+1}: Odoo sync failed")

                    except Exception as e:
                        report['errors'].append(f"Row {index+1}: {str(e)}")

                messages.success(request, f"{residence.nom} Succesfully Updated")
                messages.success(request, f"Imported {report['success']}/{report['total']} residences to Odoo")
                if report['errors']:
                    messages.warning(request, f"Errors: {', '.join(report['errors'][:3])}...")
                if last_residence:
                    return redirect('residence-detail', residence_id=last_residence.id)
                else:
                    return redirect('gestion-residence')

            except Exception as e:
                messages.warning(request, f"File error: {str(e)}")
    else:
        form = ImportExcelForm()

    if request.user.role == "Superadmin":
        residences = Residence.objects.all()
        messages.success(request, f"Residence Succesfully Updated")
    else:
        residences = Residence.objects.filter(created_by=target_profile)

    context = {
        'segment': 'import-data',
        'titlePage': 'Residence Import Data',
        'import_data_form': form,
        'profile': target_profile,
        'residences': residences,
        'date': timezone.now().strftime("%a %d %B %Y")
    }

    return HttpResponse(loader.get_template('import-data.html').render(context, request))
