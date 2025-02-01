# -*- encoding: utf-8 -*- apps/dashboard/forms.py

"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import forms

from django.utils.translation import gettext as _

from apps.authentication.models import CustomUser

from apps.residence.models import Residence

from apps.syndic.models import Syndic

from apps.supersyndic.models import SuperSyndic

from apps.coproprietaire.models import Coproprietaire

from apps.prestataire.models import Prestataire
    

class AssignSyndicForm(forms.Form):
    syndic2 = forms.ModelChoiceField(
        queryset=Syndic.objects.none(),  # Start with an empty queryset
        label=_("Syndic to Assign"),
        required=False,
        widget=forms.Select(attrs={"class": "form-control"})
    )
    supersyndic = forms.ModelChoiceField(
        queryset=SuperSyndic.objects.none(),  # Start with an empty queryset
        label=_("SuperSyndic to Assign"),
        required=False,
        widget=forms.Select(attrs={"class": "form-control"})
    )
    residence = forms.ModelChoiceField(
        queryset=Residence.objects.none(),
        label=_("Residence"),
        widget=forms.Select(attrs={"class": "form-control"})
    )

    def __init__(self, *args, **kwargs):
        residence_queryset = kwargs.pop('residence_queryset', Residence.objects.none())
        syndic_queryset = kwargs.pop('syndic_queryset', Syndic.objects.none())  # Dynamically pass syndic data
        supersyndic_queryset = kwargs.pop('supersyndic_queryset', SuperSyndic.objects.none())  # Dynamically pass supersyndic data
        super().__init__(*args, **kwargs)
        
        # Assign querysets dynamically
        self.fields['residence'].queryset = residence_queryset
        self.fields['syndic2'].queryset = syndic_queryset
        self.fields['supersyndic'].queryset = supersyndic_queryset


class RemoveSyndicForm(forms.Form):
    syndic = forms.ModelChoiceField(
        queryset=Syndic.objects.none(),
        label=_("Syndic to Remove"),
        required=False,
        widget=forms.Select(attrs={"class": "form-control"})
    )
    supersyndic = forms.ModelChoiceField(
        queryset=SuperSyndic.objects.none(),
        label=_("SuperSyndic to Remove"),
        required=False,
        widget=forms.Select(attrs={"class": "form-control"})
    )
    residence = forms.ModelChoiceField(
        queryset=Residence.objects.none(),
        label=_("Residence"),
        widget=forms.Select(attrs={"class": "form-control"})
    )

    def __init__(self, *args, **kwargs):
        residence_queryset = kwargs.pop('residence_queryset', Residence.objects.none())
        super().__init__(*args, **kwargs)

        self.fields['residence'].queryset = residence_queryset

        # Dynamically update syndic and supersyndic based on selected residence (handled via AJAX in the frontend)
        self.fields['syndic'].queryset = Syndic.objects.filter(syndic_residences__isnull=False).distinct()
        self.fields['supersyndic'].queryset = SuperSyndic.objects.filter(supersyndic_residences__isnull=False).distinct()


class AssociateToResidenceForm(forms.Form):
    syndic = forms.ModelChoiceField(
        required=False,
        queryset=Syndic.objects.none(),
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Syndic"
    )
    supersyndic = forms.ModelChoiceField(
        required=False,
        queryset=SuperSyndic.objects.none(),
        widget=forms.Select(attrs={"class": "form-control"}),
        label="SuperSyndic"
    )
    coproprietaire = forms.ModelChoiceField(
        required=False,
        queryset=Coproprietaire.objects.none(),
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Coproprietaire"
    )
    prestataire = forms.ModelChoiceField(
        required=False,
        queryset=Prestataire.objects.none(),
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Prestataire"
    )
    residence = forms.ModelChoiceField(
        queryset=Residence.objects.none(),
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Residence"
    )

    def __init__(self, *args, coproprietaire_queryset=None, prestataire_queryset=None, syndic_queryset=None, supersyndic_queryset=None, residence_queryset=None, **kwargs):
        super().__init__(*args, **kwargs)
        if coproprietaire_queryset is not None:
            self.fields['coproprietaire'].queryset = coproprietaire_queryset
            self.fields['coproprietaire'].label_from_instance = lambda obj: str(obj)
        if prestataire_queryset is not None:
            self.fields['prestataire'].queryset = prestataire_queryset
            self.fields['prestataire'].label_from_instance = lambda obj: str(obj)
        if syndic_queryset is not None:
            self.fields['syndic'].queryset = syndic_queryset
            self.fields['syndic'].label_from_instance = lambda obj: str(obj)
        if supersyndic_queryset is not None:
            self.fields['supersyndic'].queryset = supersyndic_queryset
            self.fields['supersyndic'].label_from_instance = lambda obj: str(obj)
        if residence_queryset is not None:
            self.fields['residence'].queryset = residence_queryset


class AssociateToSyndicateForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=CustomUser.objects.none(),
        label=_("Select User"),
        widget=forms.Select(attrs={"class": "form-control"}),
        required=True
    )
    syndic = forms.ModelChoiceField(
        queryset=Syndic.objects.none(),
        label=_("Select Syndic"),
        widget=forms.Select(attrs={"class": "form-control"}),
        required=False
    )
    supersyndic = forms.ModelChoiceField(
        queryset=SuperSyndic.objects.none(),
        label=_("Select Super Syndic"),
        widget=forms.Select(attrs={"class": "form-control"}),
        required=False
    )

    def __init__(self, *args, **kwargs):
        user_queryset = kwargs.pop('user_queryset', CustomUser.objects.none())
        syndic_queryset = kwargs.pop('syndic_queryset', Syndic.objects.none())
        supersyndic_queryset = kwargs.pop('supersyndic_queryset', SuperSyndic.objects.none())

        super().__init__(*args, **kwargs)

        self.fields['user'].queryset = user_queryset
        self.fields['syndic'].queryset = syndic_queryset
        self.fields['supersyndic'].queryset = supersyndic_queryset

        # Customize label to display only the user's `nom` attribute
        self.fields['user'].label_from_instance = lambda obj: obj.nom

    def save(self):
        """
        Save the associations between the selected user and syndic/supersyndic.
        """
        selected_user = self.cleaned_data.get('user')
        syndic = self.cleaned_data.get('syndic')
        supersyndic = self.cleaned_data.get('supersyndic')

        if selected_user:
            if syndic:
                selected_user.syndic_profile = syndic
            if supersyndic:
                selected_user.supersyndic_profile = supersyndic
            selected_user.save()

        return selected_user
