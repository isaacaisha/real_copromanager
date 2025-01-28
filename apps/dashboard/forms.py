# -*- encoding: utf-8 -*- apps/dashboard/forms.py

"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import forms

from apps.authentication.models import CustomUser
from apps.dashboard.models import License, Residence, SuperSyndic, Syndic, Coproprietaire, Prestataire

from django.utils.translation import gettext as _


class LicenseForm(forms.ModelForm):
    class Meta:
        model = License
        fields = ['date_debut', 'date_fin', 'fonctionnalites_personnalisees', 'est_personnalise'] # 'license_base', 
        
        # Add labels and error_messages
        labels = {
            'date_debut': _('Start Date'),
            'date_fin': _('End Date'),
            'fonctionnalites_personnalisees': _('Customized Features'),
            'est_personnalise': _('Is Customized'),
        }

        error_messages = {
            'date_debut': {
                'required': _('Start date is required.'),
            },
            'date_fin': {
                'required': _('End date is required.'),
            },
        }

        widgets = {
            # 'license_base': forms.Select(attrs={"class": "form-control"}),
            'date_debut': forms.DateInput(
                attrs={
                    "class": "form-control", 
                    "type": "date", 
                    "placeholder": _("Start Date")
                }
            ),
            'date_fin': forms.DateInput(
                attrs={
                    "class": "form-control", 
                    "type": "date", 
                    "placeholder": _("End Date")
                }
            ),
            'fonctionnalites_personnalisees': forms.TextInput(
                attrs={
                    "class": "form-control", 
                    "placeholder": _("Customized Features (optional)")
                }
            ),
            'est_personnalise': forms.CheckboxInput(
                attrs={
                    "class": "form-check-input"
                }
            ),
        }

    #def __init__(self, *args, **kwargs):
    #    super().__init__(*args, **kwargs)
    #    # Ensure the license_base queryset is active licenses
    #    self.fields['license_base'].queryset = LicenseBase.objects.all()
        

class ResidenceForm(forms.ModelForm):
    """
    Form for creating or updating a Residence.
    """
    class Meta:
        model = Residence
        fields = [
            'nom',
            'adresse',
            'nombre_appartements',
            'superficie_totale',
            'date_construction',
            'nombre_etages',
            'zones_communes',
            'date_dernier_controle',
            'type_chauffage',
        ]
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Enter building name')}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'placeholder': _('Enter address'), 'rows': 3}),
            'nombre_appartements': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('Enter number of apartments')}),
            'superficie_totale': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('Enter total area (sqm)')}),
            'date_construction': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'nombre_etages': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('Enter number of floors')}),
            'zones_communes': forms.Textarea(attrs={'class': 'form-control', 'placeholder': _('List common areas (e.g., Hall, Garden, Parking)'), 'rows': 3}),
            'date_dernier_controle': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'type_chauffage': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Enter heating type')}),
        }
        labels = {
            'nom': _('Building Name'),
            'adresse': _('Address'),
            'nombre_appartements': _('Number of Apartments'),
            'superficie_totale': _('Total Area (sqm)'),
            'date_construction': _('Construction Date'),
            'nombre_etages': _('Number of Floors'),
            'zones_communes': _('Common Areas'),
            'date_dernier_controle': _('Last Inspection Date'),
            'type_chauffage': _('Heating Type'),
        }

    def save(self, user, target_user=None, commit=True):
        residence = super().save(commit=False)

        # Automatically set the 'created_by' field to the logged-in user
        residence.created_by = user

        # Handle syndic or supersyndic associations
        try:
            if target_user:  # For residence creation with a target user
                if target_user.role in ['Syndic', 'SuperSyndic']:
                    syndic_instance = Syndic.objects.filter(user=target_user).first()
                    supersyndic_instance = SuperSyndic.objects.filter(user=target_user).first()

                    if syndic_instance:
                        residence.save()  # Save residence first before modifying ManyToMany fields
                        residence.syndic.add(syndic_instance)  # Use `.add()` for ManyToManyField
                    if supersyndic_instance:
                        residence.save()
                        residence.supersyndic.add(supersyndic_instance)
                else:
                    raise ValueError(_("Target user must be a Syndic or SuperSyndic."))
            else:  # For updates or creation without a target user
                if user.role in ['Syndic', 'SuperSyndic']:
                    syndic_instance = Syndic.objects.filter(user=user).first()
                    supersyndic_instance = SuperSyndic.objects.filter(user=user).first()

                    if syndic_instance:
                        residence.save()
                        residence.syndic.add(syndic_instance)
                    if supersyndic_instance:
                        residence.save()
                        residence.supersyndic.add(supersyndic_instance)
                elif user.role == 'Superadmin':
                    # Allow Superadmin to update without specific syndic assignment
                    pass
                else:
                    raise ValueError(_("Only Syndics or SuperSyndics can create or update residences."))
        except Syndic.DoesNotExist:
            raise ValueError(_("No Syndic instance found for the target user."))
        except SuperSyndic.DoesNotExist:
            raise ValueError(_("No SuperSyndic instance found for the target user."))

        if commit:
            residence.save()
        return residence
    

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
