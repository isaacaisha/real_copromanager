# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import template
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.template import loader
from django.urls import reverse

from apps.authentication.forms import LicenseForm
from apps.authentication.models import CustomUser
from apps.home.models import (
    License, Superadmin,
    Syndic, Coproprietaire, Prestataire, Immeuble
    )
from django.utils import timezone


@login_required(login_url="/login/")
def index(request):
    context = {
        'segment': 'index',
        'date': timezone.now().strftime("%a %d %B %Y")
        
        }
    
    try:
        superadmin = Superadmin.objects.get(user=request.user)
        context['superadmin'] = superadmin
    except Superadmin.DoesNotExist:
        context['superadmin'] = None

    try:
        syndic = Syndic.objects.get(user=request.user)
        context['syndic'] = syndic
        context['syndic_id'] = syndic.id  # Add syndic_id here
    except Syndic.DoesNotExist:
        context['syndic'] = None
        context['syndic_id'] = None

    try:
        coproprietaire = Coproprietaire.objects.get(user=request.user)
        context['coproprietaire'] = coproprietaire
        context['coproprietaire_id'] = coproprietaire.id  # Add syndic_id here
    except Coproprietaire.DoesNotExist:
        context['coproprietaire'] = None
        context['coproprietaire_id'] = None

    try:
        prestataire = Prestataire.objects.get(user=request.user)
        context['prestataire'] = prestataire
        context['prestataire_id'] = prestataire.id  # Add coproprietaire_id here
    except Prestataire.DoesNotExist:
        context['prestataire'] = None
        context['prestatairee_id'] = None

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))


# Superadmin dashboard
@login_required
@user_passes_test(lambda u: u.is_active and u.role == 'Superadmin')
def dashboard_superadmin(request):
    syndics = CustomUser.objects.filter(role='Syndic')
    coproprietaires = CustomUser.objects.filter(role='Coproprietaire')

    # Add a license field to each syndic
    for syndic in syndics:
        # Get the Syndic instance associated with the CustomUser (if exists)
        try:
            syndic_instance = Syndic.objects.get(user=syndic)
            # Retrieve the most recent license for the syndic
            syndic.license = License.objects.filter(syndic=syndic_instance).order_by('-date_debut').first()
        except Syndic.DoesNotExist:
            # Handle the case where the CustomUser is not associated with a Syndic
            syndic.license = None

    coproprietaires = CustomUser.objects.filter(role='Coproprietaire')
    prestataires = CustomUser.objects.filter(role='Prestataire')

    context = {
        'segment': 'dashboard-superadmin',
        'syndics': syndics,
        'coproprietaires': coproprietaires,
        'prestataires': prestataires,
        'titlePage': 'Dashboard Super Admin',
        'date': timezone.now().strftime("%a %d %B %Y")
    }

    html_template = loader.get_template('home/dashboard-superadmin.html')
    return HttpResponse(html_template.render(context, request))


def gestion_syndic(request):
    syndics = CustomUser.objects.filter(role='Syndic')

    # Add a license field to each syndic
    for syndic in syndics:
        # Get the Syndic instance associated with the CustomUser (if exists)
        try:
            syndic_instance = Syndic.objects.get(user=syndic)
            # Retrieve the most recent license for the syndic
            syndic.license = License.objects.filter(syndic=syndic_instance).order_by('-date_debut').first()
        except Syndic.DoesNotExist:
            # Handle the case where the CustomUser is not associated with a Syndic
            syndic.license = None

    context = {
        'segment': 'gestion-syndic',
        'syndics': syndics,
        'titlePage': 'Gestion Syndic',
        'date': timezone.now().strftime("%a %d %B %Y")
    }

    html_template = loader.get_template('home/gestion-syndic.html')
    return HttpResponse(html_template.render(context, request))


def gestion_coproprietaire(request):
    coproprietaires = CustomUser.objects.filter(role='Coproprietaire')

    context = {
        'segment': 'gestion-coproprietaire',
        'coproprietaires': coproprietaires,
        'titlePage': 'Gestion Coproprietaire',
        'date': timezone.now().strftime("%a %d %B %Y")
    }

    html_template = loader.get_template('home/gestion-coproprietaire.html')
    return HttpResponse(html_template.render(context, request))


def gestion_prestataire(request):
    prestataires = CustomUser.objects.filter(role='Prestataire')

    context = {
        'segment': 'gestion-prestataire',
        'prestataires': prestataires,
        'titlePage': 'Gestion prestataire',
        'date': timezone.now().strftime("%a %d %B %Y")
    }

    html_template = loader.get_template('home/gestion-prestataire.html')
    return HttpResponse(html_template.render(context, request))


# View for license customization
@login_required
@user_passes_test(lambda u: u.is_active and u.role == 'Superadmin')
def customize_license(request, license_id):
    license = get_object_or_404(License, id=license_id)
    if request.method == 'POST':
        license_form = LicenseForm(request.POST, instance=license)
        if license_form.is_valid():
            license.est_personnalise = license_form.cleaned_data.get('est_personnalise', True)
            license.save()
            return redirect('license-detail', license_id=license.id)
    else:
        license_form = LicenseForm(instance=license)

    context = {
        'segment': 'customize-license',
        'license_form': license_form,
        'license': license,
        'id': license.id if license else None,
        'titlePage': 'Configuration License',
        'date': timezone.now().strftime("%a %d %B %Y")
    }

    html_template = loader.get_template('home/customize-license.html')
    return HttpResponse(html_template.render(context, request))


# View to display license details
@login_required
@user_passes_test(lambda u: u.is_active and u.role == 'Superadmin')
def license_detail(request, license_id):
    license = get_object_or_404(License, id=license_id)
    syndic = license.syndic  # Access the syndic associated with this license
    coproprietaires = syndic.coproprietaire_set.all() if syndic else []
    prestataires = syndic.prestataire_set.all() if syndic else []
    immeubles = syndic.immeuble_set.all() if syndic else []
    
    context = {
        'segment': 'license-detail',
        'license': license,
        'syndic': syndic,
        'coproprietaires': coproprietaires,
        'prestataires': prestataires,
        'immeubles': immeubles,
        'titlePage': 'License Détail',
        'date': timezone.now().strftime("%a %d %B %Y")
    }
    
    html_template = loader.get_template('home/license-detail.html')
    return HttpResponse(html_template.render(context, request))


# Syndic dashboard
@login_required
@user_passes_test(lambda u: u.is_active and (u.role == 'Superadmin' or u.role == 'Syndic'))
def dashboard_syndic(request, syndic_id):
    try:
        # Fetch the current logged-in user's syndic profile
        #syndic = Syndic.objects.get(id=syndic_id)
        syndic = get_object_or_404(Syndic, id=syndic_id)

        # Retrieve relevant syndic information, such as buildings and co-owners
        immeubles = Immeuble.objects.filter(syndic=syndic)
        coproprietaires = Coproprietaire.objects.filter(syndic=syndic)
        # Retrieve the license for the logged-in syndic, handle multiple licenses if necessary
        license = License.objects.filter().order_by('-date_debut').first()
        if not license:
            messages.warning(request, 'No license found for this syndic.')
        
        context = {
            'segment': 'dashboard-syndic',
            'syndic': syndic,
            #'syndic_id': syndic_id,
            'license': license,
            'immeubles': immeubles,
            'coproprietaires': coproprietaires,
            'titlePage': 'Dashboard',
            'date': timezone.now().strftime("%a %d %B %Y")
        }

        html_template = loader.get_template('home/dashboard-syndic.html')
        return HttpResponse(html_template.render(context, request))

    except Syndic.DoesNotExist:
        # Handle the case where the syndic doesn't exist (e.g., if a user tries to access this page without being a syndic)
        context = {
            'segment': 'dashboard-syndic',
            'message': 'Syndic profile not found.',
            'titlePage': 'Dashboard',
            'date': timezone.now().strftime("%a %d %B %Y"),
        }
        
        html_template = loader.get_template('home/dashboard-syndic.html')
        return HttpResponse(html_template.render(context, request))


@login_required
@user_passes_test(lambda u: u.is_active and (u.role == 'Superadmin' or u.role == 'Coproprietaire'))
def dashboard_coproprietaire(request, coproprietaire_id):
    """
    View for the coproprietaire dashboard.
    This view should display information relevant to coproprietaires, 
    such as co-owner documents, charges, and announcements.
    """

    # Fetch the current coproprietaire profile
    if request.user.role == 'Superadmin':
        # Query by user__id when accessed by Superadmin
        coproprietaire = get_object_or_404(Coproprietaire, user__id=coproprietaire_id)
    else:
        # Query by id when accessed by Prestataire
        coproprietaire = get_object_or_404(Coproprietaire, id=coproprietaire_id)

    # Retrieve the syndic associated with this prestataire
    syndic = coproprietaire.syndic if hasattr(coproprietaire, 'syndic') else None

    # Retrieve the license associated with the syndic
    license = syndic.licence if syndic and hasattr(syndic, 'licence') else None
    
    # Retrieve all coproprietaires (if needed for the dashboard)
    coproprietaires = Coproprietaire.objects.all()
    
    context = {
        'segment': 'dashboard-coproprietaire',
        'coproprietaire': coproprietaire,
        'coproprietaires': coproprietaires,
        'titlePage': 'Dashboard',
        'date': timezone.now().strftime("%a %d %B %Y")
    }

    html_template = loader.get_template('home/dashboard-coproprietaire.html')
    return HttpResponse(html_template.render(context, request))


@login_required
@user_passes_test(lambda u: u.is_active and( u.role == 'Superadmin' or u.role == 'Prestataire'))
def dashboard_prestataire(request, prestataire_id):
    """
    View for the prestataire dashboard.
    This view should display information relevant to prestataires,
    such as assigned tasks, projects, or service requests.
    """

    # Fetch the current prestataire profile
    if request.user.role == 'Superadmin':
        # Query by user__id when accessed by Superadmin
        prestataire = get_object_or_404(Prestataire, user__id=prestataire_id)
    else:
        # Query by id when accessed by Prestataire
        prestataire = get_object_or_404(Prestataire, id=prestataire_id)

    # Retrieve the syndic associated with this prestataire
    syndic = prestataire.syndic if hasattr(prestataire, 'syndic') else None

    # Retrieve the license associated with the syndic
    license = syndic.licence if syndic and hasattr(syndic, 'licence') else None

    # Retrieve all prestataires (if needed for the dashboard)
    prestataires = Prestataire.objects.all()

    context = {
        'segment': 'dashboard-prestataire',
        'prestataire': prestataire,
        #'prestataire_id': prestataire_id,
        'prestataires': prestataires,
        'titlePage': 'Dashboard',
        'date': timezone.now().strftime("%a %d %B %Y")
    }

    html_template = loader.get_template('home/dashboard-prestataire.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def pages(request):
    context = {'date': timezone.now().strftime("%a %d %B %Y")}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    load_template = request.path.split('/')[-1]

    if load_template == 'admin':
        return HttpResponseRedirect(reverse('admin:index'))

    context['segment'] = load_template
    
    try:
        superadmin = Superadmin.objects.get(user=request.user)
        context['superadmin'] = superadmin
    except Superadmin.DoesNotExist:
        context['superadmin'] = None

    try:
        syndic = Syndic.objects.get(user=request.user)
        context['syndic'] = syndic
        context['syndic_id'] = syndic.id  # Add coproprietaire_id here
    except Syndic.DoesNotExist:
        context['syndic'] = None
        context['syndic_id'] = None

    try:
        coproprietaire = Coproprietaire.objects.get(user=request.user)
        context['coproprietaire'] = coproprietaire
        context['coproprietaire_id'] = coproprietaire.id  # Add coproprietaire_id here
    except Coproprietaire.DoesNotExist:
        context['coproprietaire'] = None
        context['coproprietaire_id'] = None

    try:
        prestataire = Prestataire.objects.get(user=request.user)
        context['prestataire'] = prestataire
        context['prestataire_id'] = prestataire.id  # Add coproprietaire_id here
    except Prestataire.DoesNotExist:
        context['prestataire'] = None
        context['prestatairee_id'] = None

    try:
        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))
    except template.TemplateDoesNotExist:
        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))
    except Exception as e:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))
