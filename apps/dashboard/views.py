# -*- encoding: utf-8 -*- apps/dashboard/views.py

"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import template
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import gettext as _
from django.contrib import messages
from django.template import loader

from django.db.models import Q  # Import Q for complex queries

from django.urls import reverse
from django.utils import timezone

from core.utils import get_user_context, otp_required_for_supersyndic  # Import the helper function

from .forms import LicenseForm, ResidenceForm
from .models import (
    License, Superadmin, SuperSyndic,
    Syndic, Coproprietaire, Prestataire, Residence
    )

from apps.authentication.forms import SuperSyndicForm
from apps.authentication.models import CustomUser


# Superadmin dashboard
@login_required(login_url="/login/")
@user_passes_test(lambda u: u.is_active and u.role == 'Superadmin')
def dashboard_superadmin(request, superadmin_id):

    # Fetch the current superadmin profile
    if request.user.role == 'Superadmin':
        # Query by user__id when accessed by Superadmin
        #superadmin = get_object_or_404(Superadmin, user__id=superadmin_id)
        #profile = get_object_or_404(Superadmin, user__id=superadmin_id)
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
        'titlePage':  _('Super Admin') + f" {request.user.nom}",
        'nom': superadmin.user.nom,
        'date': timezone.now().strftime(_("%a %d %B %Y"))
    }

    # Render template
    html_template = loader.get_template('dashboard-superadmin.html')
    return HttpResponse(html_template.render(context, request))


# Syndic dashboard
@login_required(login_url="/login/")
@user_passes_test(lambda u: u.is_active and (u.role == 'Superadmin' or u.role == 'Syndic'))
def dashboard_syndic(request, syndic_id):
    try:
        # Fetch the current syndic profile
        if request.user.role == 'Superadmin':
            # Query by user__id when accessed by Superadmin
            syndic = get_object_or_404(Syndic, user__id=syndic_id)
            profile = get_object_or_404(Syndic, user__id=syndic_id)
        else:
            # Restrict to the currently logged-in syndic
            syndic = get_object_or_404(Syndic, user=request.user)
            profile = get_object_or_404(Syndic, user=request.user)

        # Retrieve relevant syndic information, such as buildings and co-owners
        residences = Residence.objects.filter(syndic=syndic)
        coproprietaires = Coproprietaire.objects.filter(syndic=syndic)
        prestataires = Prestataire.objects.filter(syndic=syndic)
        # Retrieve the license for the logged-in syndic, handle multiple licenses if necessary
        license = License.objects.filter(syndic=syndic).order_by('-date_debut').first()
        if not license:
            messages.warning(request, _('No license found for this syndic.'))
        
        context = {
            'segment': 'dashboard-syndic',
            'syndic': syndic,
            'profile': profile,
            'license': license,
            'coproprietaires': coproprietaires,
            'prestataires': prestataires,
            'residences': residences,
            'titlePage': _('Dashboard') + f" {syndic.user.nom}",
            'nom': syndic.user.nom,
            'phone': syndic.user.phone,
            'date': timezone.now().strftime(_("%a %d %B %Y"))
        }

        html_template = loader.get_template('dashboard-syndic.html')
        return HttpResponse(html_template.render(context, request))

    except Syndic.DoesNotExist:
        # Handle the case where the syndic doesn't exist (e.g., if a user tries to access this page without being a syndic)
        context = {
            'segment': 'dashboard-syndic',
            'titlePage': _('Dashboard'),
            'date': timezone.now().strftime(_("%a %d %B %Y")),
        }
        
        html_template = loader.get_template('dashboard-syndic.html')
        return HttpResponse(html_template.render(context, request))


# View for the Super User page, requiring 2FA status
@login_required(login_url="/login/")
@otp_required_for_supersyndic
@user_passes_test(lambda u: u.is_active and (u.role == 'Superadmin' or u.role == 'SuperSyndic'))
def dashboard_supersyndic(request, supersyndic_id):

    # Fetch the current logged-in user's syndic profile
    try:
        # Fetch the current syndic profile
        if request.user.role == 'Superadmin':
            # Query by user__id when accessed by Superadmin
            supersyndic = get_object_or_404(SuperSyndic, user__id=supersyndic_id)
            profile = get_object_or_404(SuperSyndic, user__id=supersyndic_id)
        else:
            # Restrict to the currently logged-in syndic
            supersyndic = get_object_or_404(SuperSyndic, user=request.user)
            profile = get_object_or_404(SuperSyndic, user=request.user)

        ## Retrieve relevant syndic information, such as buildings and co-owners
        #residences = Residence.objects.filter(supersyndic=supersyndic)
        residences = Residence.objects.filter(supersyndic=supersyndic)
        coproprietaires = Coproprietaire.objects.filter(supersyndic=supersyndic)
        prestataires = Prestataire.objects.filter(supersyndic=supersyndic)
            
        # Retrieve the license for the logged-in syndic, handle multiple licenses if necessary
        license = License.objects.filter(supersyndic=supersyndic).order_by('-date_debut').first()
        if not license:
            messages.warning(request, _('No license found for this syndic.'))
        
        context = {
            'segment': 'dashboard-supersyndic',
            'supersyndic': supersyndic,
            'profile': profile,
            'license': license,
            'residences': residences,
            'coproprietaires': coproprietaires,
            'prestataires': prestataires,
            'titlePage': _('Super Syndic') + f" {supersyndic.user.nom}",
            'nom': supersyndic.user.nom,
            'phone': supersyndic.user.phone,
            'date': timezone.now().strftime(_("%a %d %B %Y"))
        }

        html_template = loader.get_template('dashboard-supersyndic.html')
        return HttpResponse(html_template.render(context, request))

    except SuperSyndic.DoesNotExist:
        # Handle the case where the syndic doesn't exist (e.g., if a user tries to access this page without being a syndic)
        context = {
            'segment': 'dashboard-supersyndic',
            'titlePage': _('Dashboard'),
            'date': timezone.now().strftime(_("%a %d %B %Y")),
        }
        
        html_template = loader.get_template('dashboard-supersyndic.html')
        return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
@user_passes_test(lambda u: u.is_active and u.role in ['Superadmin', 'Syndic', 'SuperSyndic', 'Coproprietaire'])
def dashboard_coproprietaire(request, coproprietaire_id):
    """
    View for the coproprietaire dashboard.
    This view should display information relevant to coproprietaires, 
    such as co-owner documents, charges, and announcements.
    """

    # Fetch the current coproprietaire profile  
    if request.user.role in ['Superadmin', 'Syndic', 'SuperSyndic']:
        # Allow Superadmin, Syndic, and SuperSyndic to query by user__id
        coproprietaire = get_object_or_404(Coproprietaire, user__id=coproprietaire_id)
        profile = get_object_or_404(Coproprietaire, user__id=coproprietaire_id)
    elif request.user.role == 'Coproprietaire':
        # Restrict to the currently logged-in coproprietaire
        coproprietaire = get_object_or_404(Coproprietaire, user=request.user)
        profile = get_object_or_404(Coproprietaire, user=request.user)
    else:
        # Forbid access for other roles
        return HttpResponse(status=403)
    
    # Retrieve the syndic or supersyndic associated with this prestataire
    syndic = coproprietaire.syndic if hasattr(coproprietaire, 'syndic') else None
    supersyndic = coproprietaire.supersyndic if hasattr(coproprietaire, 'supersyndic') else None

    # Retrieve the license associated with the syndic or supersyndic
    license = syndic.licence if syndic and hasattr(syndic, 'license') else None
    #license = supersyndic.licence if supersyndic and hasattr(supersyndic, 'license') else None
    
     # Only fetch the coproprietaires associated with the current syndic
    if request.user.role == 'Superadmin':
        coproprietaires = Coproprietaire.objects.all()  # Superadmin can see all
    elif request.user.role == ['Syndic']:
        coproprietaires = Coproprietaire.objects.filter(syndic=syndic)
    elif request.user.role == ['SuperSyndic']:
        coproprietaires = Coproprietaire.objects.filter(supersyndic=supersyndic)
    else:
        coproprietaires = Coproprietaire.objects.filter(user=request.user)

    # Calculate the total count
    total_count = coproprietaires.count()

    context = {
        'segment': 'dashboard-coproprietaire',
        'titlePage': _('Dashboard') + f" {coproprietaire.user.nom}",
        'profile': profile,
        'coproprietaire': coproprietaire,
        'coproprietaires': coproprietaires,
        'syndic': syndic,
        'supersyndic': supersyndic,
        'license': license,
        'nom': coproprietaire.user.nom,
        'phone': coproprietaire.user.phone,
        'total_count': total_count,
        'date': timezone.now().strftime(_("%a %d %B %Y"))
    }

    html_template = loader.get_template('dashboard-coproprietaire.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
@user_passes_test(lambda u: u.is_active and u.role in ['Superadmin', 'Syndic', 'SuperSyndic', 'Prestataire'])
def dashboard_prestataire(request, prestataire_id):
    """
    View for the prestataire dashboard.
    This view should display information relevant to prestataires,
    such as assigned tasks, projects, or service requests.
    """

    # Fetch the current prestataire profile
    if request.user.role in ['Superadmin', 'Syndic', 'SuperSyndic']:
        # Query by user__id when accessed by Superadmin
        prestataire = get_object_or_404(Prestataire, user__id=prestataire_id)
        profile = get_object_or_404(Prestataire, user__id=prestataire_id)
    elif request.user.role == 'Prestataire':
        # Restrict to the currently logged-in prestataire
        prestataire = get_object_or_404(Prestataire, user=request.user)
        profile = get_object_or_404(Prestataire, user=request.user)
    else:
        return HttpResponse(status=403)

    # Retrieve the syndic or supersyndic associated with this prestataire
    syndic = prestataire.syndic if hasattr(prestataire, 'syndic') else None
    supersyndic = prestataire.supersyndic if hasattr(prestataire, 'supersyndic') else None

    # Retrieve the license associated with the syndic or supersyndic
    license = syndic.licence if syndic and hasattr(syndic, 'license') else None
    #license = supersyndic.licence if supersyndic and hasattr(supersyndic, 'license') else None
    
    # Only fetch the prestataires associated with the current syndic
    if request.user.role == 'Superadmin':
        prestataires = Prestataire.objects.all()  # Superadmin can see all
    elif request.user.role == ['Syndic']:
        prestataires = Prestataire.objects.filter(syndic=syndic)
    elif request.user.role == ['SuperSyndic']:
        prestataires = Prestataire.objects.filter(supersyndic=supersyndic)
    else:
        prestataires = Prestataire.objects.filter(user=request.user)

    # Calculate the total count
    total_count = prestataires.count()

    context = {
        'segment': 'dashboard-prestataire',
        'titlePage': _('Dashboard') + f" {prestataire.user.nom}",
        'profile': profile,
        'prestataire': prestataire,
        'prestataires': prestataires,
        'syndic': syndic,
        'supersyndic': supersyndic,
        'license': license,
        'nom': prestataire.user.nom,
        'phone': prestataire.user.phone,
        'total_count': total_count,
        'date': timezone.now().strftime(_("%a %d %B %Y"))
    }

    html_template = loader.get_template('dashboard-prestataire.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
@user_passes_test(lambda u: u.is_active and u.role in ['Superadmin', 'Syndic', 'SuperSyndic'])
def gestion_residence(request):
    """
    View for managing SuperSyndic users.
    Only accessible to users with the role of 'Superadmin', 'Syndic', or 'SuperSyndic'.
    """
    # Add a license field to each syndic
    try:
        license = request.user.licences.first()  # Assuming the user has a related 'licences' field
    except AttributeError:
        license = None  # Handle cases where the user has no associated license

    # Filter residences based on the user's role and related field
    if request.user.role == 'Syndic':
        if not hasattr(request.user, 'syndic_profile'):
            messages.error(request, _("You are not authorized to view this page."))
        residences = Residence.objects.filter(syndic=request.user.syndic_profile)
        coproprietaires = Coproprietaire.objects.filter(syndic=request.user.syndic_profile)
        prestataires = Prestataire.objects.filter(syndic=request.user.syndic_profile)
    elif request.user.role == 'SuperSyndic':
        if not hasattr(request.user, 'supersyndic_profile'):
            messages.error(request, _("You are not authorized to view this page."))
        residences = Residence.objects.filter(syndic=request.user.syndic_profile)
        coproprietaires = Coproprietaire.objects.filter(syndic=request.user.syndic_profile)
        prestataires = Prestataire.objects.filter(supersyndic=request.user.supersyndic_profile)
    else:  # For Superadmin or other roles, display all residences
        residences = Residence.objects.all()
        coproprietaires = Coproprietaire.objects.all()
        prestataires = Prestataire.objects.all()

    context = {
        'segment': 'gestion-residence',
        'license': license,  # Ensure 'license' is defined before adding to context
        'residences': residences,
        'coproprietaires': coproprietaires,
        'prestataires': prestataires,
        'titlePage': _('Residence Gestion'),
        'nom': request.user.nom,
        'date': timezone.now().strftime(_("%a %d %B %Y"))
    }

    html_template = loader.get_template('gestion-residence.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
@user_passes_test(lambda u: u.is_active and u.role == 'Superadmin')
def gestion_syndic(request):
    form = SuperSyndicForm()
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
        'form': form,
        'syndics': syndics,
        'titlePage': _('Syndic Gestion'),
        'nom': request.user.nom,
        'date': timezone.now().strftime(_("%a %d %B %Y"))
    }

    html_template = loader.get_template('gestion-syndic.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
@user_passes_test(lambda u: u.is_active and u.role == 'Superadmin')
def gestion_supersyndic(request):
    """
    View for managing SuperSyndic users.
    Only accessible to users with the role of 'Superadmin'.
    """
    # Get all SuperSyndic users
    supersyndics = CustomUser.objects.filter(role='SuperSyndic')

    # Attach related license data to each super_syndic
    for supersyndic in supersyndics:
        try:
            supersyndic_instance = SuperSyndic.objects.get(user=supersyndic)
            # Retrieve the most recent license for the super_syndic
            supersyndic.license = License.objects.filter(
                supersyndic=supersyndic_instance
            ).order_by('-date_debut').first()
        except SuperSyndic.DoesNotExist:
            # Handle the case where the CustomUser is not associated with a SuperSyndic
            supersyndic.license = None

    context = {
        'segment': 'gestion-supersyndic',
        'supersyndics': supersyndics,
        'titlePage': _('Super Syndic Gestion'),
        'nom': request.user.nom,
        'date': timezone.now().strftime(_("%a %d %B %Y")),
    }

    html_template = loader.get_template('gestion-supersyndic.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
@user_passes_test(lambda u: u.is_active and u.role in ['Superadmin', 'Syndic', 'SuperSyndic'])
def gestion_coproprietaire(request):
    # Filter coproprietaires based on the user's role
    if request.user.role == 'Syndic':
        if not hasattr(request.user, 'syndic_profile'):
            messages.error(request, _("You are not authorized to view this page."))
        coproprietaires = Coproprietaire.objects.filter(syndic=request.user.syndic_profile)
        prestataires = Prestataire.objects.filter(syndic=request.user.syndic_profile)
    elif request.user.role == 'SuperSyndic':
        if not hasattr(request.user, 'supersyndic_profile'):
            messages.error(request, _("You are not authorized to view this page."))
        coproprietaires = Coproprietaire.objects.filter(supersyndic=request.user.supersyndic_profile)
        prestataires = Prestataire.objects.filter(supersyndic=request.user.supersyndic_profile)
    else:  # Superadmin can view all Coproprietaires
        coproprietaires = Coproprietaire.objects.all()
        prestataires = Prestataire.objects.all()

    # Calculate the total count
    total_count = coproprietaires.count() + prestataires.count()

    context = {
        'segment': 'gestion-coproprietaire',
        'coproprietaires': coproprietaires,
        'prestataires': prestataires,
        'total_count': total_count,
        'titlePage': _('Coproprietaire Gestion'),
        'nom': request.user.nom,
        'date': timezone.now().strftime(_("%a %d %B %Y"))
    }

    html_template = loader.get_template('gestion-coproprietaire.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
@user_passes_test(lambda u: u.is_active and u.role in ['Superadmin', 'Syndic', 'SuperSyndic'])
def gestion_prestataire(request):
    # Filter coproprietaires based on the user's role
    if request.user.role == 'Syndic':
        if not hasattr(request.user, 'syndic_profile'):
            messages.error(request, _("You are not authorized to view this page."))
        prestataires = Prestataire.objects.filter(syndic=request.user.syndic_profile)
        coproprietaires = Coproprietaire.objects.filter(syndic=request.user.syndic_profile)
    elif request.user.role == 'SuperSyndic':
        if not hasattr(request.user, 'supersyndic_profile'):
            messages.error(request, _("You are not authorized to view this page."))
        prestataires = Prestataire.objects.filter(supersyndic=request.user.supersyndic_profile)
        coproprietaires = Coproprietaire.objects.filter(supersyndic=request.user.supersyndic_profile)
    else:  # Superadmin can view all Coproprietaires
        prestataires = Prestataire.objects.all()
        coproprietaires = Coproprietaire.objects.all()

    # Calculate the total count
    total_count = coproprietaires.count() + prestataires.count()

    context = {
        'segment': 'gestion-prestataire',
        'prestataires': prestataires,
        'coproprietaires': coproprietaires,
        'total_count': total_count,
        'titlePage': _('Prestataire Gestion'),
        'nom': request.user.nom,
        'date': timezone.now().strftime(_("%a %d %B %Y"))
    }

    html_template = loader.get_template('gestion-prestataire.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
@user_passes_test(lambda u: u.is_active and (u.role == 'Superadmin' or u.role in ['Syndic', 'SuperSyndic']))
def create_residence(request, user_id):
    """
    Create a new residence. Allows a Superadmin to create a residence for a syndic or supersyndic.
    """
    try:
        # Determine the acting user and the target profile
        if request.user.role == 'Superadmin':
            profile = CustomUser.objects.get(id=user_id)  # Target Syndic or SuperSyndic
        elif request.user.role in ['Syndic', 'SuperSyndic']:
            profile = request.user  # Acting Syndic or SuperSyndic
        else:
            messages.error(request, _("You do not have permission to create a residence."))
            return redirect('home')

        if request.method == "POST":
            residence_form = ResidenceForm(request.POST)
            if residence_form.is_valid():
                # Pass the profile to the save method explicitly
                residence = residence_form.save(user=request.user)
                messages.success(request, _('Residence created successfully: ') + f"{residence.nom}")
                return redirect('residence-detail', user_id)
        else:
            residence_form = ResidenceForm()

        # Context and rendering
        context = {
            'segment': 'create-residence',
            'residence_form': residence_form,
            'profile': profile,
            'titlePage': _('Residence Creation'),
            'nom': profile.nom if hasattr(profile, 'nom') else '',
            'date': timezone.now().strftime(_("%a %d %B %Y")),
        }

        html_template = loader.get_template('create-residence.html')
        return HttpResponse(html_template.render(context, request))

    except CustomUser.DoesNotExist:
        messages.error(request, _("User not found."))
        return redirect('home')
    except ValueError as e:
        messages.error(request, str(e))
        return redirect('home')


@login_required(login_url="/login/")
@user_passes_test(lambda u: u.is_active and (u.role == 'Superadmin' or u.role in ['Syndic', 'SuperSyndic']))
def update_residence(request, residence_id):
    """
    Update an existing residence.
    Allows a user to update a residence they created or manage.
    """
    residence = get_object_or_404(Residence, id=residence_id)

    # Check if the user is authorized to edit this residence
    if request.user.role == 'Syndic' and residence.syndic != request.user:
        messages.error(request, _("You do not have permission to edit this residence."))
        return redirect('update-residence', residence_id)
    if request.user.role == 'SuperSyndic' and residence.supersyndic != request.user:
        messages.error(request, _("You do not have permission to edit this residence."))
        return redirect('update-residence', residence_id)

    if request.method == "POST":
        residence_form = ResidenceForm(request.POST, instance=residence)
        if residence_form.is_valid():
            residence = residence_form.save(user=request.user)
            messages.success(request, _('Residence updated successfully: ') + f"{residence.nom}")
            return redirect('residence-detail', residence_id=residence.id)
        else:
            messages.error(request, _("Please correct the errors below."))
    else:
        residence_form = ResidenceForm(instance=residence)

    # Render the form for editing
    context = {
        'segment': 'update-residence',
        'residence_form': residence_form,
        'residence': residence,
        'titlePage': _('Update Residence'),
        'nom': request.user.nom,
        'date': timezone.now().strftime(_("%a %d %B %Y")),
    }

    html_template = loader.get_template('update-residence.html')
    return HttpResponse(html_template.render(context, request))


# View to display license details
@login_required(login_url="/login/")
#@user_passes_test(lambda u: u.is_active and u.role == 'Superadmin')
def residence_detail(request, residence_id):
    residence = get_object_or_404(Residence, id=residence_id)

    # Filter coproprietaires based on the user's role
    if request.user.role == 'Syndic':
        if not hasattr(request.user, 'syndic_profile'):
            messages.error(request, _("You are not authorized to view this page."))
        residences = Residence.objects.filter(syndic=request.user.syndic_profile)
        coproprietaires = Coproprietaire.objects.filter(syndic=request.user.syndic_profile)
        prestataires = Prestataire.objects.filter(syndic=request.user.syndic_profile)
    elif request.user.role == 'SuperSyndic':
        if not hasattr(request.user, 'supersyndic_profile'):
            messages.error(request, _("You are not authorized to view this page."))
        residences = Residence.objects.filter(supersyndic=request.user.supersyndic_profile)
        coproprietaires = Coproprietaire.objects.filter(supersyndic=request.user.supersyndic_profile)
        prestataires = Prestataire.objects.filter(supersyndic=request.user.supersyndic_profile)
    else:  # Superadmin can view all Coproprietaires
        residences = Residence.objects.all()
        coproprietaires = Coproprietaire.objects.all()
        prestataires = Prestataire.objects.all()

    # Calculate the total count
    total_count = coproprietaires.count() + prestataires.count()
    
    context = {
        'segment': 'license-detail',
        'residence': residence,
        'coproprietaires': coproprietaires,
        'prestataires': prestataires,
        'residences': residences,
        'total_count': total_count,
        'titlePage': _('Residence Details') + f" n° {residence.id}",
        'nom': request.user.nom,
        'date': timezone.now().strftime(_("%a %d %B %Y"))
    }
    
    html_template = loader.get_template('residence-detail.html')
    return HttpResponse(html_template.render(context, request))


# View for license customization
@login_required(login_url="/login/")
@user_passes_test(lambda u: u.is_active and u.role == 'Superadmin')
def customize_license(request, license_id):
    license = get_object_or_404(License, id=license_id)
    if request.method == 'POST':
        license_form = LicenseForm(request.POST, instance=license)
        if license_form.is_valid():
            license.est_personnalise = license_form.cleaned_data.get('est_personnalise', True)
            license.save()
            messages.success(request, _('Updated successfully') + f" License: {license.id}")
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
        'titlePage': _('License Configuration') + f" n° {license.id}",
        'nom': request.user.nom,
        'date': timezone.now().strftime(_("%a %d %B %Y"))
    }

    html_template = loader.get_template('customize-license.html')
    return HttpResponse(html_template.render(context, request))


# View to display license details
@login_required(login_url="/login/")
@user_passes_test(lambda u: u.is_active and u.role == 'Superadmin')
def license_detail(request, license_id):
    license = get_object_or_404(License, id=license_id)
    syndic = license.syndic  # Access the syndic associated with this license
    supersyndic = license.supersyndic
    coproprietaires = syndic.coproprietaire_set.all() if syndic else []
    prestataires = syndic.prestataire_set.all() if syndic else []
    residences = None
    
    context = {
        'segment': 'license-detail',
        'license': license,
        'syndic': syndic,
        'supersyndic': supersyndic,
        'coproprietaires': coproprietaires,
        'prestataires': prestataires,
        'residences': residences,
        'titlePage': _('License Details') + f" n° {license.id}",
        'nom': request.user.nom,
        'date': timezone.now().strftime(_("%a %d %B %Y"))
    }
    
    html_template = loader.get_template('license-detail.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
@user_passes_test(lambda u: u.is_active and u.role in ['Superadmin', 'Syndic', 'SuperSyndic'])
def user_search(request):
    query = request.GET.get('q', '').strip()  # Get the search query from the GET request
    
    # Filter by 'nom' or 'email', case-insensitive
    users = CustomUser.objects.filter(
        Q(nom__icontains=query) | Q(email__icontains=query)
    )

    context = {
        'users': users,
        'query': query,
        'titlePage': _('Result for: "%s"') % query,
        'nom': request.user.nom,
        'date': timezone.now().strftime(_("%a %d %B %Y"))
    }
    
    html_template = loader.get_template('search-results.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def user_profile(request, user_id):
    # Initialize variables
    superadmin = None
    syndic = None
    supersyndic = None
    license = None
    residences = None
    coproprietaire = None
    prestataire = None
    coproprietaires = None
    prestataires = None
    user = get_object_or_404(CustomUser, id=user_id)  # Get the user by ID

    # Fetch role-specific data
    if user.role == 'Superadmin':
        superadmin = get_object_or_404(Superadmin, user=user)
        profile = get_object_or_404(Superadmin, user=user)

    elif user.role == 'Syndic':
        syndic = get_object_or_404(Syndic, user=user)
        profile = get_object_or_404(Syndic, user=user)

        residences = Residence.objects.filter(syndic=syndic)
        # Retrieve the license associated with the syndic
        license = License.objects.filter(syndic=syndic).order_by('-date_debut').first()
        # Fetch associated coproprietaires
        coproprietaires = Coproprietaire.objects.filter(syndic=syndic)
        # Fetch associated prestataires
        prestataires = Prestataire.objects.filter(syndic=syndic)

    elif user.role == 'SuperSyndic':
        supersyndic = get_object_or_404(SuperSyndic, user=user)
        profile = get_object_or_404(SuperSyndic, user=user)

        residences = Residence.objects.filter(supersyndic=supersyndic)
        license = License.objects.filter(supersyndic=supersyndic).order_by('-date_debut').first()
        # Fetch associated coproprietaires
        coproprietaires = Coproprietaire.objects.filter(supersyndic=supersyndic)
        # Fetch associated prestataires
        prestataires = Prestataire.objects.filter(supersyndic=supersyndic)

    elif user.role == 'Coproprietaire':
        coproprietaire = get_object_or_404(Coproprietaire, user=user)
        profile = get_object_or_404(Coproprietaire, user=user)
        syndic = coproprietaire.syndic if hasattr(coproprietaire, 'syndic') else None
        supersyndic = coproprietaire.supersyndic if hasattr(coproprietaire, 'supersyndic') else None

    elif user.role == 'Prestataire':
        prestataire = get_object_or_404(Prestataire, user=user)
        profile = get_object_or_404(Prestataire, user=user)
        syndic = prestataire.syndic if hasattr(prestataire, 'syndic') else None
        supersyndic = prestataire.supersyndic if hasattr(prestataire, 'supersyndic') else None

    context = {
        'profile': profile,
        'residences': residences,
        'nom': user.nom,
        'superadmin': superadmin,
        'syndic': syndic,
        'supersyndic': supersyndic,
        'license': license,
        'coproprietaire': coproprietaire,
        'prestataire': prestataire,
        'coproprietaires': coproprietaires,
        'prestataires': prestataires,
        'titlePage': _('Profile of %s') % user.nom,
        'date': timezone.now().strftime(_("%a %d %B %Y")),
    }

    html_template = loader.get_template('user-profile.html')
    return HttpResponse(html_template.render(context, request))
