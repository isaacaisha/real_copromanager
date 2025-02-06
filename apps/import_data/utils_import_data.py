# -*- encoding: utf-8 -*- apps/import_data/utils_import_data.py

# -*- encoding: utf-8 -*-
import datetime
import re
import pandas as pd
import magic

from django.utils.translation import gettext as _
from django.core.files.storage import default_storage
from django.core.exceptions import ValidationError
from django.core.cache import cache
from django.conf import settings

from apps.residence.models import Residence


def parse_excel_date(value):
    """Handle both string dates and Excel serial dates.
    Returns a date object or None.
    """
    try:
        if pd.isnull(value) or str(value).strip() == "":
            return None
        if isinstance(value, (int, float)):  # Excel serial dates
            return (datetime.datetime(1899, 12, 30) + datetime.timedelta(days=value)).date()
        return pd.to_datetime(value).date()
    except Exception as e:
        print(f"Date parsing error for value {value}: {e}")
        return None

def to_int(value, default=0):
    try:
        if pd.isnull(value) or str(value).strip() == "":
            return default
        return int(value)
    except Exception:
        return default

def to_float(value, default=0.0):
    try:
        if pd.isnull(value) or str(value).strip() == "":
            return default
        return float(value)
    except Exception:
        return default

def validate_excel_file(file):
    mime = magic.Magic(mime=True)
    file_type = mime.from_buffer(file.read(1024))
    file.seek(0)  # Reset cursor

    allowed_types = [
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # .xlsx
        "text/csv"  # .csv
    ]

    if file_type not in allowed_types:
        raise ValidationError("Seuls les fichiers .xlsx et .csv sont autorisés.")

def clean_excel_data(file):
    df = pd.read_excel(file)
    print("Original DataFrame columns:", df.columns.tolist())  # Debugging print

    df = df.applymap(lambda x: '' if isinstance(x, str) and x.startswith(('=', '@')) else x)

    dangerous_patterns = [r"<script.*?>.*?</script>", r"DROP TABLE", r"DELETE FROM", r"INSERT INTO"]
    df = df.applymap(lambda x: re.sub("|".join(dangerous_patterns), "", x) if isinstance(x, str) else x)

    max_rows = 5000
    if len(df) > max_rows:
        raise ValueError("Le fichier dépasse la limite autorisée de 5000 lignes.")
    
    return df

def handle_uploaded_file(file):
    file_path = f"{settings.MEDIA_ROOT}/tmp/{file.name}"
    path = default_storage.save(file_path, file)

    # Process file
    cleaned_data = clean_excel_data(default_storage.open(path))

    # Delete after processing
    default_storage.delete(path)
    return cleaned_data

def limit_imports(user):
    key = f"import_count_{user.id}"
    import_count = cache.get(key, 0)

    if import_count >= 10:
        raise Exception("Limite d’import atteinte, veuillez réessayer plus tard.")

    cache.set(key, import_count + 1, timeout=3600)  # 10 imports per hour

def save_data_to_db(cleaned_df, target_profile):
    for _, row in cleaned_df.iterrows():
        Residence.objects.update_or_create(
            nom=row["Nom"].strip().title(),
            adresse=row["Adresse"].strip().title(),
            defaults={
                "nombre_appartements": int(row.get('Nombre Appartements', 0)),
                "superficie_totale": float(row.get('Superficie Totale', 0.0)),
                "date_construction": row.get('Date Construction'),
                "nombre_etages": int(row.get('Nombre Etages', 0)),
                "zones_communes": row.get('Zones Communes', ""),
                "date_dernier_controle": row.get('Date Dernier Contrôle'),
                "type_chauffage": row.get('Type Chauffage', ""),
                "created_by": target_profile
            }
        )
