# -*- encoding: utf-8 -*- apps/import_data/forms.py

"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import forms


class ImportExcelForm(forms.Form):
    file = forms.FileField(label="Select Excel File")
    