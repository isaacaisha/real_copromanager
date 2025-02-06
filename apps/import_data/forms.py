# -*- encoding: utf-8 -*- apps/import_data/forms.py

"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import forms

from apps.import_data.utils_import_data import validate_excel_file


class ImportExcelForm(forms.Form):
    file = forms.FileField(validators=[validate_excel_file], label="Select Excel File")
    