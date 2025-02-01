# -*- encoding: utf-8 -*- apps/dashboard/views.py

"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import gettext as _
from django.contrib import messages
from django.template import loader

from django.db.models import Q  # Import Q for complex queries

from django.utils import timezone

from apps.authentication.models import CustomUser

from .models import License, Superadmin

from .forms import LicenseForm

from apps.syndic.models import Syndic

from apps.supersyndic.models import SuperSyndic


# Superadmin dashboard
@login_required(login_url="/login/")
@user_passes_test(lambda u: u.is_active and u.role in ['Superadmin'])
def dashboard_superadmin(request, superadmin_id):

    # Fetch the current superadmin profile
    if request.user.role == 'Superadmin':
        superadmin = get_object_or_404(Superadmin, user=request.user)
        profile = get_object_or_404(Superadmin, user=request.user)
    else:
        return HttpResponse(status=403)
    
    # Retrieve all Super Syndics, Syndics, and other roles
    supersyndics = CustomUser.objects.filter(role='SuperSyndic')
    syndics = CustomUser.objects.filter(role='Syndic')
    coproprietaires = CustomUser.objects.filter(role='Coproprietaire')
    prestataires = CustomUser.objects.filter(role='Prestataire')

    # Add a license field to each Super Syndic
    for supersyndic in supersyndics:
        try:
            supersyndic_instance = SuperSyndic.objects.get(user=supersyndic)
            # Retrieve the most recent license for the Super Syndic
            supersyndic.license = (
                License.objects.filter(supersyndic=supersyndic_instance)
                .order_by('-date_debut')
                .first()
            )
        except SuperSyndic.DoesNotExist:
            # Handle the case where the CustomUser is not associated with a SuperSyndic
            supersyndic.license = None

    # Add a license field to each syndic
    for syndic in syndics:
        try:
            # Retrieve the Syndic instance
            syndic_instance = Syndic.objects.get(user=syndic)
            # Retrieve the most recent license for the Syndic
            syndic.license = (
                License.objects.filter(syndic=syndic_instance)
                .order_by('-date_debut')
                .first()
            )
        except Syndic.DoesNotExist:
            # Handle the case where the CustomUser is not associated with a Syndic
            syndic.license = None

    # Prepare context
    context = {
        'segment': 'dashboard-superadmin',
        'profile': profile,
        'supersyndics': supersyndics,
        'syndics': syndics,
        'coproprietaires': coproprietaires,
        'prestataires': prestataires,
        'titlePage':  _('Super Admin "%s"') % request.user.nom,
        'nom': superadmin.user.nom,
        'date': timezone.now().strftime(_("%a %d %B %Y"))
    }

    # Render template
    html_template = loader.get_template('dashboard-superadmin.html')
    return HttpResponse(html_template.render(context, request))


# View for license customization
@login_required(login_url="/login/")
@user_passes_test(lambda u: u.is_active and u.role in ['Superadmin'])
def customize_license(request, license_id):
    license = get_object_or_404(License, id=license_id)
    if request.method == 'POST':
        license_form = LicenseForm(request.POST, instance=license)
        if license_form.is_valid():
            license.est_personnalise = license_form.cleaned_data.get('est_personnalise', True)
            license.save()
            messages.success(request, _('License n° "%s" Updated successfully') % license.id)
            return redirect('license-detail', license_id=license.id)
        else:
            messages.error(request, _("There were errors in the form. Please correct them."))
    else:
        license_form = LicenseForm(instance=license)

    context = {
        'segment': 'customize-license',
        'license_form': license_form,
        'license': license,
        'id': license.id if license else None,
        'titlePage': _('Configuration License n° "%s"') % license.id,
        'nom': request.user.nom,
        'date': timezone.now().strftime(_("%a %d %B %Y"))
    }

    html_template = loader.get_template('customize-license.html')
    return HttpResponse(html_template.render(context, request))


# View to display license details
@login_required(login_url="/login/")
@user_passes_test(lambda u: u.is_active and u.role in ['Superadmin'])
def license_detail(request, license_id):
    license = get_object_or_404(License, id=license_id)
    syndic = license.syndic  # Access the syndic associated with this license
    supersyndic = license.supersyndic
    coproprietaires = syndic.syndic_coproprietaires.all() if syndic else []
    prestataires = syndic.syndic_prestataires.all() if syndic else []
    residences = None
    
    context = {
        'segment': 'license-detail',
        'license': license,
        'syndic': syndic,
        'supersyndic': supersyndic,
        'coproprietaires': coproprietaires,
        'prestataires': prestataires,
        'residences': residences,
        'titlePage': _('Details License n° "%s"') % license.id,
        'nom': request.user.nom,
        'date': timezone.now().strftime(_("%a %d %B %Y"))
    }
    
    html_template = loader.get_template('license-detail.html')
    return HttpResponse(html_template.render(context, request))
