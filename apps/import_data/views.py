# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import datetime
import pandas as pd

from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import gettext as _
from django.contrib import messages
from django.utils import timezone

from apps.authentication.models import CustomUser
from apps.residence.models import Residence
from apps.syndic.models import Syndic
from apps.supersyndic.models import SuperSyndic
from .forms import ImportExcelForm

def parse_excel_date(value):
    """Handle both string dates and Excel serial dates.
    Returns a date object or None.
    """
    try:
        if pd.isnull(value) or str(value).strip() == "":
            return None
        
        # Handle Excel serial dates (numbers)
        if isinstance(value, (int, float)):
            return (datetime.datetime(1899, 12, 30) + datetime.timedelta(days=value)).date()
            
        # Handle string dates and datetime objects
        return pd.to_datetime(value).date()
        
    except Exception as e:
        print(f"Date parsing error for value {value}: {e}")
        return None

@login_required
@user_passes_test(lambda u: u.is_active and u.role in ['Superadmin', 'Syndic', 'SuperSyndic'])
def import_residences(request, user_id=None):
    # Determine the target profile (if Superadmin passes a user_id, import for that user)
    if request.user.role == "Superadmin" and user_id:
        profile = get_object_or_404(CustomUser, id=user_id)
    else:
        profile = request.user

    if request.method == "POST":
        form = ImportExcelForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                df = pd.read_excel(request.FILES['file'])
                
                # DEBUG: Print out the Excel column names.
                print("Excel columns:", df.columns.tolist())
                
                report = {'success': 0, 'errors': [], 'total': len(df)}

                for index, row in df.iterrows():
                    try:
                        # Validate required fields using explicit checks:
                        def validate_field(field_name, value):
                            if value is None or pd.isnull(value) or str(value).strip() == "":
                                raise ValueError(f"Missing required field: {field_name}")
                            return str(value).strip()

                        # IMPORTANT: Make sure the header here matches your Excel file.
                        nom_residence = validate_field('Nom Résidence', row.get('Nom de la Résidence'))
                        adresse = validate_field('Adresse', row.get('Adresse'))
                        
                        # If your Excel header for the date is different (for example "Date de Construction")
                        # update the key accordingly.
                        date_construction = parse_excel_date(row.get('Date Construction'))
                        if date_construction is None:
                            raise ValueError("Missing required field: Date Construction")

                        # Create the Residence record.
                        residence = Residence.objects.create(
                            nom=nom_residence,
                            adresse=adresse,
                            nombre_appartements=int(row.get('Nombre Appartements', 0)),
                            superficie_totale=float(row.get('Superficie Totale', 0)),
                            date_construction=date_construction,
                            nombre_etages=int(row.get('Nombre Etages', 0)),
                            zones_communes=row.get('Zones Communes', ''),
                            date_dernier_controle=parse_excel_date(row.get('Date Dernier Contrôle')),
                            type_chauffage=row.get('Type Chauffage', ''),
                            created_by=request.user
                        )

                        # Auto-assign relationships based on the target profile's role.
                        if profile.role == 'Syndic':
                            try:
                                syndic = Syndic.objects.get(user=profile)
                                residence.syndic.add(syndic)
                            except Syndic.DoesNotExist:
                                messages.warning(request, f"No Syndic record found for {profile.nom}")
                        elif profile.role == 'SuperSyndic':
                            try:
                                supersyndic = SuperSyndic.objects.get(user=profile)
                                residence.supersyndic.add(supersyndic)
                            except SuperSyndic.DoesNotExist:
                                messages.warning(request, f"No SuperSyndic record found for {profile.nom}")

                        # Process additional Syndic relationships (comma-separated in the "Syndics" column).
                        syndic_field = row.get('Syndics', '')
                        if syndic_field and not pd.isnull(syndic_field):
                            for name in syndic_field.split(','):
                                name = name.strip()
                                if name:
                                    syndic, _ = Syndic.objects.get_or_create(nom=name)
                                    residence.syndic.add(syndic)

                        # Process additional SuperSyndic relationships (comma-separated in the "SuperSyndics" column).
                        supersyndic_field = row.get('SuperSyndics', '')
                        if supersyndic_field and not pd.isnull(supersyndic_field):
                            for name in supersyndic_field.split(','):
                                name = name.strip()
                                if name:
                                    supersyndic, _ = SuperSyndic.objects.get_or_create(nom=name)
                                    residence.supersyndic.add(supersyndic)

                        # Sync with Odoo (assuming Residence.sync_to_odoo() is implemented).
                        if residence.sync_to_odoo():
                            report['success'] += 1
                        else:
                            report['errors'].append(f"Row {index+1}: Odoo sync failed")

                    except Exception as e:
                        report['errors'].append(f"Row {index+1}: {str(e)}")

                # Generate report.
                messages.success(request, f"Imported {report['success']}/{report['total']} residences")
                if report['errors']:
                    messages.error(request, f"Errors: {', '.join(report['errors'][:3])}...")

                return redirect('import-residences', profile.id)

            except Exception as e:
                messages.error(request, f"File error: {str(e)}")
    else:
        form = ImportExcelForm()

    context = {
        'segment': 'import-data',
        'import_data_form': form,
        'profile': profile,
        #'date': timezone.now().strftime(_("%a %d %B %Y"))
    }

    return HttpResponse(loader.get_template('import-data.html').render(context, request))
