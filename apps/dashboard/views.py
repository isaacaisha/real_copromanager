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

from .forms import (
    LicenseForm, ResidenceForm, AssignSyndicForm, RemoveSyndicForm,
    AssociateToResidenceForm, AssociateToSyndicateForm
    )
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
        # Calculate the total count
        total_count = coproprietaires.count() + prestataires.count()

        # Retrieve the license for the logged-in syndic, handle multiple licenses if necessary
        license = License.objects.filter(syndic=syndic).order_by('-date_debut').first()
        if not license:
            messages.warning(request, _('No license found for this syndic.'))
        
        context = {
            'segment': 'dashboard-syndic',
            'titlePage': _('Dashboard "%s"') % syndic.user.nom,
            'syndic': syndic,
            'profile': profile,
            'license': license,
            'residences': residences,
            'coproprietaires': coproprietaires,
            'prestataires': prestataires,
            'total_count': total_count,
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
        # Calculate the total count
        total_count = coproprietaires.count() + prestataires.count()
            
        # Retrieve the license for the logged-in syndic, handle multiple licenses if necessary
        license = License.objects.filter(supersyndic=supersyndic).order_by('-date_debut').first()
        if not license:
            messages.warning(request, _('No license found for this syndic.'))
        
        context = {
            'segment': 'dashboard-supersyndic',
            'titlePage': _('Super Syndic "%s"') % supersyndic.user.nom,
            'supersyndic': supersyndic,
            'profile': profile,
            'license': license,
            'residences': residences,
            'coproprietaires': coproprietaires,
            'prestataires': prestataires,
            'total_count': total_count,
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
    such as co-owner documents, charges, announcements, and residences.
    """

    # Fetch the current coproprietaire profile  
    if request.user.role in ['Superadmin', 'Syndic', 'SuperSyndic']:
        # Allow Superadmin, Syndic, and SuperSyndic to query by user__id
        coproprietaire = get_object_or_404(Coproprietaire, user__id=coproprietaire_id)
    elif request.user.role == 'Coproprietaire':
        # Restrict to the currently logged-in coproprietaire
        coproprietaire = get_object_or_404(Coproprietaire, user=request.user)
    else:
        # Forbid access for other roles
        return HttpResponse(status=403)
    
    # Fetch all residences associated with the coproprietaire
    residences = coproprietaire.residence.all()

    # Retrieve syndic and supersyndic associated with this coproprietaire
    syndics = coproprietaire.syndic.all()
    supersyndics = coproprietaire.supersyndic.all()

    ## Retrieve the licenses associated with the syndics and supersyndics
    #syndic_licenses = [syndic.licence for syndic in syndics if hasattr(syndic, 'licence')]
    #supersyndic_licenses = [supersyndic.licence for supersyndic in supersyndics if hasattr(supersyndic, 'licence')]
#
    ## Combine all licenses into a single list (if needed)
    #licenses = syndic_licenses + supersyndic_licenses
    
    # Fetch the coproprietaires associated with the current syndic
    coproprietaires = None
    if request.user.role in ['Syndic', 'Superadmin']:
        # If syndic_set has multiple entries, query for all associated coproprietaires
        coproprietaires = Coproprietaire.objects.filter(syndic__in=syndics).distinct()
    elif request.user.role == 'SuperSyndic':
        # If supersyndic_set has multiple entries, query for all associated coproprietaires
        coproprietaires = Coproprietaire.objects.filter(supersyndic__in=supersyndics).distinct()
    elif request.user.role == 'Coproprietaire':
        coproprietaires = Coproprietaire.objects.filter(user=request.user)

    # Convert ManyRelatedManager fields to lists or querysets explicitly
    coproprietaires = list(coproprietaires) if coproprietaires else []

    # Calculate the total count
    total_count = len(coproprietaires)

    context = {
        'segment': 'dashboard-coproprietaire',
        'titlePage': _('Dashboard "%s"') % coproprietaire.user.nom,
        'coproprietaire': coproprietaire,
        'residences': residences,
        'coproprietaires': coproprietaires,
        'syndics': syndics,
        'supersyndics': supersyndics,
        #'licenses': licenses,
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
    
    # Fetch all residences associated with the prestataire
    residences = prestataire.residence.all()

    # Retrieve the syndic or supersyndic associated with this prestataire
    syndics = prestataire.syndic.all()
    supersyndics = prestataire.supersyndic.all()

    ## Retrieve the licenses associated with the syndics and supersyndics
    #syndic_licenses = [syndic.licence for syndic in syndics if hasattr(syndic, 'licence')]
    #supersyndic_licenses = [supersyndic.licence for supersyndic in supersyndics if hasattr(supersyndic, 'licence')]
#
    ## Combine all licenses into a single list (if needed)
    #licenses = syndic_licenses + supersyndic_licenses

    # Only fetch the prestataires associated with the current syndic
    if request.user.role == ['Syndic']:
        prestataires = Prestataire.objects.filter(syndic__in=syndics).distinct()
        coproprietaires = Coproprietaire.objects.filter(syndic__in=syndics).distinct()
    elif request.user.role == ['SuperSyndic']:
        prestataires = Prestataire.objects.filter(supersyndic__in=supersyndics).distinct()
        coproprietaires = Coproprietaire.objects.filter(supersyndic__in=supersyndics).distinct()
    else:
        prestataires = Prestataire.objects.all()
        coproprietaires = Coproprietaire.objects.all()

    # Calculate the total count
    total_count_presta = prestataires.count()

    context = {
        'segment': 'dashboard-prestataire',
        'titlePage': _('Dashboard "%s"') % prestataire.user.nom,
        'profile': profile,
        'prestataire': prestataire,
        'prestataires': prestataires,
        'coproprietaires': coproprietaires,
        'residences': residences,
        'syndics': syndics,
        'supersyndics': supersyndics,
        #'licenses': licenses,
        'nom': prestataire.user.nom,
        'phone': prestataire.user.phone,
        'total_count_presta': total_count_presta,
        'date': timezone.now().strftime(_("%a %d %B %Y"))
    }

    html_template = loader.get_template('dashboard-prestataire.html')
    return HttpResponse(html_template.render(context, request))
    

@login_required(login_url="/login/")
@user_passes_test(lambda u: u.is_active and u.role in ['Superadmin', 'Syndic', 'SuperSyndic'])
def gestion_residence(request):
    """
    View for managing residences.
    - Superadmin can see all Syndic and SuperSyndic related data.
    - Syndics and SuperSyndics see only their own residences.
    """
    try:
        if request.user.role == 'Syndic':
            syndic_profile = getattr(request.user, 'syndic_profile', None)
            if syndic_profile is None:
                messages.error(request, _("You are not authorized to view this page."))
                return HttpResponse(status=403)
            residences = Residence.objects.filter(syndic=syndic_profile)
            coproprietaires = Coproprietaire.objects.filter(syndic=syndic_profile)
            prestataires = Prestataire.objects.filter(syndic=syndic_profile)

        elif request.user.role == 'SuperSyndic':
            supersyndic_profile = getattr(request.user, 'supersyndic_profile', None)
            if supersyndic_profile is None:
                messages.error(request, _("You are not authorized to view this page."))
                return HttpResponse(status=403)
            residences = Residence.objects.filter(supersyndic=supersyndic_profile)
            coproprietaires = Coproprietaire.objects.filter(supersyndic=supersyndic_profile)
            prestataires = Prestataire.objects.filter(supersyndic=supersyndic_profile)

        elif request.user.role == 'Superadmin':
            # For Superadmin or other roles, display all residences
            residences = Residence.objects.all()
            coproprietaires = Coproprietaire.objects.all()
            prestataires = Prestataire.objects.all()
            
        else:
            messages.error(request, _("You are not authorized to view this page."))
            return HttpResponse(status=403)

        # Context for the template
        context = {
            'segment': 'gestion-residence',
            'license': request.user.licences.first() if hasattr(request.user, 'licences') else None,
            'residences': residences,
            'coproprietaires': coproprietaires,
            'prestataires': prestataires,
            'titlePage': _('Residence Gestion'),
            'nom': request.user.nom,
            'date': timezone.now().strftime(_("%a %d %B %Y")),
        }

        html_template = loader.get_template('gestion-residence.html')
        return HttpResponse(html_template.render(context, request))

    except Syndic.DoesNotExist:
        messages.error(request, _("The requested syndic does not exist."))
        return HttpResponse(status=404)


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
@user_passes_test(lambda u: u.is_active and u.role in ['Superadmin', 'Syndic', 'SuperSyndic'])
def create_residence(request, user_id):
    try:
        profile = None
        if request.user.role == 'Superadmin':  # For Superadmin, target a specific user
            profile = CustomUser.objects.filter(id=user_id, role__in=['Syndic', 'SuperSyndic']).first()
            if not profile:
                messages.error(request, _("Target user must be a Syndic or SuperSyndic."))
                return redirect('home')
        else:
            profile = request.user  # For Syndic or SuperSyndic, target themselves

        if request.method == "POST":
            residence_form = ResidenceForm(request.POST)
            if residence_form.is_valid():
                residence = residence_form.save(user=request.user, target_user=profile)
                messages.success(request, _('Residence "%s" created successfully.') % residence.nom)
                return redirect('residence-detail', residence_id=residence.id)
            else:
                messages.error(request, _("Please correct the errors below."))
        else:
            residence_form = ResidenceForm()

        context = {
            'segment': 'create-residence',
            'titlePage': _('Residence Creation'),
            'profile': profile,
            'residence_form': residence_form,
        }

        html_template = loader.get_template('create-residence.html')
        return HttpResponse(html_template.render(context, request))

    except Exception as e:
        messages.error(request, _("An unexpected error occurred: %s") % str(e))
        return redirect('home')


@login_required(login_url="/login/")
@user_passes_test(lambda u: u.is_active and u.role in ['Superadmin', 'Syndic', 'SuperSyndic'])
def update_residence(request, residence_id):
    residence = get_object_or_404(Residence, id=residence_id)

    if request.method == "POST":
        residence_form = ResidenceForm(request.POST, instance=residence)
        if residence_form.is_valid():
            try:
                residence = residence_form.save(user=request.user)
                messages.success(request, _('Residence "%s" updated successfully.') % residence.nom)
                return redirect('residence-detail', residence_id=residence.id)
            except ValueError as e:
                messages.error(request, str(e))
        else:
            messages.error(request, _("Please correct the errors below."))
    else:
        residence_form = ResidenceForm(instance=residence)

    context = {
        'segment': 'update-residence',
        'residence_form': residence_form,
        'residence': residence,
        'titlePage': _('Update Residence "%s"') % residence.nom,
    }

    html_template = loader.get_template('update-residence.html')
    return HttpResponse(html_template.render(context, request))


# View to display residence details
@login_required(login_url="/login/")
@user_passes_test(lambda u: u.is_active and u.role in ['Superadmin', 'Syndic', 'SuperSyndic'])
def residence_detail(request, residence_id):
    residence = get_object_or_404(Residence, id=residence_id)

    # Initialize empty querysets
    residences = Residence.objects.none()
    coproprietaires = Coproprietaire.objects.none()
    prestataires = Prestataire.objects.none()

    # Filter data based on user role
    if request.user.role == 'Syndic':
        if hasattr(request.user, 'syndic_profile'):
            residences = Residence.objects.filter(syndic=request.user.syndic_profile)
            coproprietaires = Coproprietaire.objects.filter(residence__id=residence.id)
            prestataires = Prestataire.objects.filter(residence__id=residence.id)
        else:
            messages.error(request, _("You are not authorized to view this page."))
            return redirect('home')

    elif request.user.role == 'SuperSyndic':
        if hasattr(request.user, 'supersyndic_profile'):
            residences = Residence.objects.filter(supersyndic=request.user.supersyndic_profile)
            coproprietaires = Coproprietaire.objects.filter(residence__id=residence.id)
            prestataires = Prestataire.objects.filter(residence__id=residence.id)
        else:
            messages.error(request, _("You are not authorized to view this page."))
            return redirect('home')

    elif request.user.role == 'Superadmin':
        residences = Residence.objects.all()
        coproprietaires = Coproprietaire.objects.filter(residence=residence)
        prestataires = Prestataire.objects.filter(residence=residence)

    else:
        messages.error(request, _("You are not authorized to view this page."))
        return redirect('home')

    # Calculate the total count of related objects
    total_count = coproprietaires.count() + prestataires.count()

    # Prepare context for the template
    context = {
        'segment': 'license-detail',
        'residence': residence,
        'coproprietaires': coproprietaires,
        'prestataires': prestataires,
        'residences': residences,
        'total_count': total_count,
        'titlePage': _('Residence "%s" Details') % residence.nom,
        'syndics': residence.syndic.all() if hasattr(residence, 'syndic') else None,
        'supersyndics': residence.supersyndic.all() if hasattr(residence, 'supersyndic') else None,
        'nom': request.user.nom,
        'date': timezone.now().strftime(_("%a %d %B %Y"))
    }

    # Render the template
    html_template = loader.get_template('residence-detail.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
@user_passes_test(lambda u: u.is_active and u.role in ['Superadmin'])
def assign_syndic_to_residence(request):
    residences = Residence.objects.all()  # Allow Superadmin to manage all residences
    syndic_queryset = Syndic.objects.filter(user__is_active=True)  # All active syndics
    supersyndic_queryset = SuperSyndic.objects.filter(user__is_active=True)  # All active supersyndics

    # Handle POST request
    if request.method == "POST":
        form = AssignSyndicForm(
            request.POST,
            residence_queryset=residences,
            syndic_queryset=syndic_queryset,
            supersyndic_queryset=supersyndic_queryset

        )
        if form.is_valid():
            residence = form.cleaned_data['residence']
            syndic2 = form.cleaned_data.get('syndic2')
            supersyndic = form.cleaned_data.get('supersyndic')

            # Add syndic and/or supersyndic to the residence without removing existing assignments
            if syndic2:
                residence.syndic.add(syndic2)
                messages.success(
                request,
                _("{syndic2} successfully assigned to Residence {res_name}.").format(
                    syndic2=syndic2.nom, res_name=residence.nom
                )
            )
            if supersyndic:
                residence.supersyndic.add(supersyndic)
                messages.success(
                request,
                _("{supersyndic} successfully assigned to Residence {res_name}.").format(
                    supersyndic=supersyndic.user.nom, res_name=residence.nom
                )
            )
                
            return redirect('residence-detail', residence.id)
        else:
            messages.error(request, _("Form is not valid. Please correct the errors."))
    else:
        form = AssignSyndicForm(
            residence_queryset=residences,
            syndic_queryset=syndic_queryset,
            supersyndic_queryset=supersyndic_queryset
        )

    # Add coproprietaires for the first residence (or selected residence) to the context
    coproprietaires = None
    if residences.exists():
        coproprietaires = residences.first().coproprietaire_residences.all()

    # Render the template
    context = {
        'segment': 'assign-syndic',
        "titlePage": _("Assign Syndicate with a Residence"),
        "form": form,
        'residences': residences,
        'coproprietaires': coproprietaires,
        'date': timezone.now().strftime(_("%a %d %B %Y"))
    }

    html_template = loader.get_template('assign-syndic.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
@user_passes_test(lambda u: u.is_active and u.role == 'Superadmin')
def remove_syndic_from_residence(request):
    residences = Residence.objects.all()
    
    if request.method == "POST":
        form = RemoveSyndicForm(request.POST, residence_queryset=residences)
        if form.is_valid():
            residence = form.cleaned_data['residence']
            syndic = form.cleaned_data.get('syndic')
            supersyndic = form.cleaned_data.get('supersyndic')

            if syndic:
                residence.syndic.remove(syndic)
                messages.success(
                    request,
                    _("{syndic} successfully removed from Residence {res_name}.").format(
                        syndic=syndic.nom, res_name=residence.nom
                    )
                )

            if supersyndic:
                residence.supersyndic.remove(supersyndic)
                messages.success(
                    request,
                    _("{supersyndic} successfully removed from Residence {res_name}.").format(
                        supersyndic=supersyndic.user.nom, res_name=residence.nom
                    )
                )

            return redirect('residence-detail', residence.id)
        else:
            messages.error(request, _("Form is not valid. Please correct the errors."))
    else:
        form = RemoveSyndicForm(residence_queryset=residences)

    context = {
        'segment': 'remove-syndic',
        "titlePage": _("Remove Syndic from Residence"),
        "form": form,
        'residences': residences,
        'date': timezone.now().strftime(_("%a %d %B %Y"))
    }

    html_template = loader.get_template('remove-syndic.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
@user_passes_test(lambda u: u.is_active and u.role in ['Superadmin', 'Syndic', 'SuperSyndic'])
def remove_user_from_residence(request, residence_id, user_id, role):
    """
    Allows:
      - Superadmins to remove anyone.
      - Syndics to remove SuperSyndics, other Syndics, Copropriétaires, and Prestataires (but not themselves).
      - SuperSyndics to remove other SuperSyndics, Syndics, Copropriétaires, and Prestataires (but not themselves).
    """
    try:
        residence = get_object_or_404(Residence, id=residence_id)
        current_user = request.user

        # Superadmin can remove anyone
        if current_user.role == "Superadmin":
            if role == "syndic":
                syndic = get_object_or_404(Syndic, user_id=user_id)
                residence.syndic.remove(syndic)
                messages.success(request, _("'{syndic}' successfully removed from Residence {res_name}.").format(
                    res_name=residence.nom, syndic=syndic.nom
                ))
            elif role == "supersyndic":
                supersyndic = get_object_or_404(SuperSyndic, user_id=user_id)
                residence.supersyndic.remove(supersyndic)
                messages.success(request, _("'{supersyndic}' successfully removed from Residence {res_name}.").format(
                    res_name=residence.nom, supersyndic=supersyndic.nom
                ))
            elif role == "coproprietaire":
                coproprietaire = get_object_or_404(Coproprietaire, user_id=user_id)
                residence.coproprietaire_residences.remove(coproprietaire)
                messages.success(request, _("'{coproprietaire}' successfully removed from Residence {res_name}.").format(
                    res_name=residence.nom, coproprietaire=coproprietaire.user.nom
                ))
            elif role == "prestataire":
                prestataire = get_object_or_404(Prestataire, user_id=user_id)
                residence.prestataire_residences.remove(prestataire)
                messages.success(request, _("'{prestataire}' successfully removed from Residence {res_name}.").format(
                    res_name=residence.nom, prestataire=prestataire.user.nom
                ))

        # Syndics can remove SuperSyndics, other Syndics, Copropriétaires, and Prestataires (but not themselves)
        elif current_user.role == "Syndic" and hasattr(current_user, "syndic_profile"):
            syndic_profile = current_user.syndic_profile

            if syndic_profile in residence.syndic.all():
                if role == "syndic":
                    syndic_to_remove = get_object_or_404(Syndic, user_id=user_id)
                    if syndic_to_remove != syndic_profile:
                        residence.syndic.remove(syndic_to_remove)
                        messages.success(request, _("'{syndic_to_remove}' successfully removed from Residence {res_name}.").format(
                        res_name=residence.nom, syndic_to_remove=syndic_to_remove.nom
                    ))
                    else:
                        messages.warning(request, _("'%s' You cannot remove yourself.") % syndic_to_remove.nom)
                elif role == "supersyndic":
                    supersyndic_to_remove = get_object_or_404(SuperSyndic, user_id=user_id)
                    residence.supersyndic.remove(supersyndic_to_remove)
                    messages.success(request, _("'{supersyndic_to_remove}' successfully removed from Residence {res_name}.").format(
                        res_name=residence.nom, supersyndic_to_remove=supersyndic_to_remove.nom
                    ))
                elif role == "coproprietaire":
                    coproprietaire = get_object_or_404(Coproprietaire, user_id=user_id)
                    residence.coproprietaire_residences.remove(coproprietaire)
                    messages.success(request, _("'{coproprietaire}' successfully removed from Residence {res_name}.").format(
                        res_name=residence.nom, coproprietaire=coproprietaire.user.nom
                    ))
                elif role == "prestataire":
                    prestataire = get_object_or_404(Prestataire, user_id=user_id)
                    residence.prestataire_residences.remove(prestataire)
                    messages.success(request, _("'{prestataire}' successfully removed from Residence {res_name}.").format(
                        res_name=residence.nom, prestataire=prestataire.user.nom
                    ))
                else:
                    messages.error(request, _("Invalid role specified."))

            else:
                messages.error(request, _("You are not authorized to modify this residence."))

        # SuperSyndics can remove Syndics, other SuperSyndics, Copropriétaires, and Prestataires (but not themselves)
        elif current_user.role == "SuperSyndic" and hasattr(current_user, "supersyndic_profile"):
            supersyndic_profile = current_user.supersyndic_profile

            if supersyndic_profile in residence.supersyndic.all():
                if role == "supersyndic":
                    supersyndic_to_remove = get_object_or_404(SuperSyndic, user_id=user_id)
                    if supersyndic_to_remove != supersyndic_profile:
                        residence.supersyndic.remove(supersyndic_to_remove)
                        messages.success(request, _("'{supersyndic_to_remove}' successfully removed from Residence {res_name}.").format(
                            res_name=residence.nom, supersyndic_to_remove=supersyndic_to_remove.nom
                        ))
                    else:
                        messages.warning(request, _("'%s' You cannot remove yourself.") % supersyndic_to_remove.nom)
                elif role == "syndic":
                    syndic_to_remove = get_object_or_404(Syndic, user_id=user_id)
                    residence.syndic.remove(syndic_to_remove)
                    messages.success(request, _("'{syndic_to_remove}' successfully removed from Residence {res_name}.").format(
                        res_name=residence.nom, syndic_to_remove=syndic_to_remove.nom
                    ))
                elif role == "coproprietaire":
                    coproprietaire = get_object_or_404(Coproprietaire, user_id=user_id)
                    residence.coproprietaire_residences.remove(coproprietaire)
                    messages.success(request, _("'{coproprietaire}' successfully removed from Residence {res_name}.").format(
                        res_name=residence.nom, coproprietaire=coproprietaire.user.nom
                    ))
                elif role == "prestataire":
                    prestataire = get_object_or_404(Prestataire, user_id=user_id)
                    residence.prestataire_residences.remove(prestataire)
                    messages.success(request, _("'{prestataire}' successfully removed from Residence {res_name}.").format(
                        res_name=residence.nom, prestataire=prestataire.user.nom
                    ))
                else:
                    messages.error(request, _("Invalid role specified."))

            else:
                messages.error(request, _("You are not authorized to modify this residence."))

        else:
            messages.error(request, _("You are not authorized to perform this action."))

    except (Residence.DoesNotExist, Syndic.DoesNotExist, SuperSyndic.DoesNotExist, Coproprietaire.DoesNotExist, Prestataire.DoesNotExist):
        messages.error(request, _("Residence or user not found."))

    return redirect('residence-detail', residence.id)  # Redirect to residence details


@login_required(login_url="/login/")
@user_passes_test(lambda u: u.is_active and u.role in ['Syndic', 'SuperSyndic'])
def associate_to_residence(request):
    residences = Residence.objects.none()
    coproprietaires = Coproprietaire.objects.none()
    prestataires = Prestataire.objects.none()
    syndics = Syndic.objects.none()
    supersyndics = SuperSyndic.objects.none()

    if request.user.role == 'Syndic' and hasattr(request.user, 'syndic_profile'):
        syndic_profile = request.user.syndic_profile
        residences = Residence.objects.filter(syndic=syndic_profile)
        
        # Only include coproprietaires and prestataires linked to these syndic_profile
        coproprietaires = Coproprietaire.objects.filter(syndic=syndic_profile)
        prestataires = Prestataire.objects.filter(syndic=syndic_profile)

        # Only show syndics linked to these residences
        syndics = Syndic.objects.filter(syndic_residences__in=residences).exclude(pk=syndic_profile.pk).distinct()
        
        # Retrieve the associated SuperSyndic(s) for the residences
        supersyndics = SuperSyndic.objects.filter(supersyndic_residences__in=residences).distinct()

    elif request.user.role == 'SuperSyndic' and hasattr(request.user, 'supersyndic_profile'):
        supersyndic_profile = request.user.supersyndic_profile
        residences = Residence.objects.filter(supersyndic=supersyndic_profile)
        
        # Only include coproprietaires and prestataires linked to these supersyndic_profile
        coproprietaires = Coproprietaire.objects.filter(supersyndic=supersyndic_profile)
        prestataires = Prestataire.objects.filter(supersyndic=supersyndic_profile)

        # Syndics assigned to residences under this SuperSyndic
        syndics = Syndic.objects.filter(residence__in=residences).distinct()

        # SuperSyndics associated with residences under the same management
        supersyndics = SuperSyndic.objects.filter(supersyndic_residences__in=residences).exclude(pk=supersyndic_profile.pk).distinct()

    else:
        messages.error(request, _("You are not authorized to perform this action."))
        return redirect('home')

    if request.method == "POST":
        form = AssociateToResidenceForm(
            request.POST,
            coproprietaire_queryset=coproprietaires,
            prestataire_queryset=prestataires,
            residence_queryset=residences,
            syndic_queryset=syndics,
            supersyndic_queryset=supersyndics
        )
        if form.is_valid():
            coproprietaire = form.cleaned_data.get('coproprietaire')
            prestataire = form.cleaned_data.get('prestataire')
            syndic = form.cleaned_data.get('syndic')
            supersyndic = form.cleaned_data.get('supersyndic')
            residence = form.cleaned_data['residence']

            if coproprietaire:
                coproprietaire.residence.add(residence)
                coproprietaire.save()
                messages.success(request, _("Coproprietaire '%s' associated successfully.") % coproprietaire.user.nom)

            if prestataire:
                prestataire.residence.add(residence)
                prestataire.save()
                messages.success(request, _("Prestataire '%s' associated successfully.") % prestataire.user.nom)

            if syndic:
                residence.syndic.add(syndic)
                residence.save()
                messages.success(request, _("Syndic '%s' associated successfully.") % syndic.user.nom)

            if supersyndic:
                residence.supersyndic.add(supersyndic)
                residence.save()
                messages.success(request, _("SuperSyndic '%s' associated successfully.") % supersyndic.user.nom)

            return redirect('residence-detail', residence.id)
        else:
            messages.error(request, _("Form is not valid. Please correct the errors."))
    else:
        form = AssociateToResidenceForm(
            coproprietaire_queryset=coproprietaires,
            prestataire_queryset=prestataires,
            residence_queryset=residences,
            syndic_queryset=syndics,
            supersyndic_queryset=supersyndics
        )

    context = {
        'segment': 'associate-co-users-to-residence',
        "titlePage": _("Associate Co-Users with a Residence"),
        "form": form,
        'date': timezone.now().strftime(_("%a %d %B %Y"))
    }

    html_template = loader.get_template('associate-to-residence.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
@user_passes_test(lambda u: u.is_active and u.role in ['Syndic', 'SuperSyndic'])
def associate_to_syndicate(request):
    # Determine user role and associated residences
    associated_residences = None
    syndic_queryset = Syndic.objects.none()
    supersyndic_queryset = SuperSyndic.objects.none()

    if request.user.role == 'Syndic' and hasattr(request.user, 'syndic_profile'):
        associated_residences = Residence.objects.filter(syndic=request.user.syndic_profile)
        syndic_queryset = Syndic.objects.filter(syndic_residences__in=associated_residences).distinct()
        supersyndic_queryset = SuperSyndic.objects.filter(supersyndic_residences__in=associated_residences).distinct()
    elif request.user.role == 'SuperSyndic' and hasattr(request.user, 'supersyndic_profile'):
        associated_residences = Residence.objects.filter(supersyndic=request.user.supersyndic_profile)
        supersyndic_queryset = SuperSyndic.objects.filter(supersyndic_residences__in=associated_residences).distinct()
        syndic_queryset = Syndic.objects.filter(syndic_residences__in=associated_residences).distinct()
    else:
        messages.error(request, _("You are not authorized to perform this action."))
        return redirect('home')

    # Query users related to the residences and only fetch their names
    if not syndic_queryset:
        copro_residence_users = CustomUser.objects.none()
    else:
        copro_residence_users = CustomUser.objects.filter(
            Q(coproprietaire_profile__syndic=request.user.syndic_profile) |
            Q(prestataire_profile__syndic=request.user.syndic_profile)
        ).distinct()

    if not supersyndic_queryset:
        presta_residence_users = CustomUser.objects.none()
    else:
        presta_residence_users = CustomUser.objects.filter(
            Q(coproprietaire_profile__supersyndic=request.user.supersyndic_profile) |
            Q(prestataire_profile__supersyndic=request.user.supersyndic_profile)
        ).distinct()

    # Combine the results
    residence_users = copro_residence_users | presta_residence_users
    
    # Handle form submission
    if request.method == "POST":
        form = AssociateToSyndicateForm(
            request.POST,
            user_queryset=residence_users,
            syndic_queryset=syndic_queryset,
            supersyndic_queryset=supersyndic_queryset,
        )
        if form.is_valid():
            selected_user = form.save()  # Delegate saving logic to the form
            syndic = form.cleaned_data.get('syndic')
            supersyndic = form.cleaned_data.get('supersyndic')

            if selected_user:
                if syndic:
                    # Associate the user with the syndic
                    selected_user.syndic_profile = syndic
                    selected_user.save()

                    # If they are a 'Coproprietaire' (Co-owner), add them to the syndic's residences
                    if hasattr(selected_user, 'coproprietaire_profile'):
                        selected_user.coproprietaire_profile.syndic.add(syndic)
                        selected_user.coproprietaire_profile.save()

                    # If they are a 'Prestataire' (Provider), add them to the syndic's residences
                    if hasattr(selected_user, 'prestataire_profile'):
                        selected_user.prestataire_profile.syndic.add(syndic)
                        selected_user.prestataire_profile.save()

                    messages.success(
                        request,
                        _("'{user_name}' successfully associated with '{syndic_name}'.").format(
                            user_name=selected_user.nom, syndic_name=syndic.nom
                        )
                    )
                    return redirect('dashboard-syndic', syndic.id)

                if supersyndic:
                    # Associate the user with the supersyndic
                    selected_user.supersyndic_profile = supersyndic
                    selected_user.save()

                    # If they are a 'Coproprietaire' (Co-owner), add them to the supersyndic's residences
                    if hasattr(selected_user, 'coproprietaire_profile'):
                        selected_user.coproprietaire_profile.syndic.add(supersyndic)
                        selected_user.coproprietaire_profile.save()

                    # If they are a 'Prestataire' (Provider), add them to the supersyndic's residences
                    if hasattr(selected_user, 'prestataire_profile'):
                        selected_user.prestataire_profile.syndic.add(supersyndic)
                        selected_user.prestataire_profile.save()

                    messages.success(
                        request,
                        _("'{user_name}' successfully associated with '{supersyndic_name}'.").format(
                            user_name=selected_user.nom, supersyndic_name=supersyndic.nom
                        )
                    )
                    return redirect('dashboard-supersyndic', supersyndic.id)

            else:
                messages.error(request, _("No valid user selected."))
        else:
            messages.error(request, _("Form is not valid. Please correct the errors."))
    else:
        # Initialize the form with dynamic querysets
        form = AssociateToSyndicateForm(
            user_queryset=residence_users,
            syndic_queryset=syndic_queryset,
            supersyndic_queryset=supersyndic_queryset
        )

    # Render the template
    context = {
        'segment': 'associate-co-users-to-syndicate',
        "titlePage": _("Associate Co-Users with a Syndicate"),
        "form": form,
        'date': timezone.now().strftime(_("%a %d %B %Y"))
    }

    html_template = loader.get_template('associate-to-syndicate.html')
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
@user_passes_test(lambda u: u.is_active and u.role == 'Superadmin')
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


@login_required(login_url="/login/")
@user_passes_test(lambda u: u.is_active and u.role in ['Superadmin', 'Syndic', 'SuperSyndic', 'Coproprietaire', 'Prestataire'])
def user_search(request):
    query = request.GET.get('q', '').strip()  # Get the search query
    user = request.user

    # Default empty querysets
    users = CustomUser.objects.none()
    residences = Residence.objects.none()

    if user.role == 'Superadmin':
        # Superadmin sees everything
        users = CustomUser.objects.all()
        residences = Residence.objects.all()

    else:
        # Fetch associated residences first
        if user.role == 'Syndic' and hasattr(user, 'syndic_profile'):
            residences = Residence.objects.filter(syndic=user.syndic_profile)
        elif user.role == 'SuperSyndic' and hasattr(user, 'supersyndic_profile'):
            residences = Residence.objects.filter(supersyndic=user.supersyndic_profile)
        elif user.role == 'Coproprietaire' and hasattr(user, 'coproprietaire_profile'):
            residences = Residence.objects.filter(coproprietaire_residences=user.coproprietaire_profile)
        elif user.role == 'Prestataire' and hasattr(user, 'prestataire_profile'):
            residences = Residence.objects.filter(prestataires_residences=user.prestataire_profile)

        # Filter users who are part of the same residences
        users = CustomUser.objects.filter(
            Q(coproprietaire_profile__residence__in=residences) |
            Q(prestataire_profile__residence__in=residences) |
            Q(syndic_profile__syndic_residences__in=residences) |
            Q(supersyndic_profile__supersyndic_residences__in=residences)
        ).distinct()

    # Apply search query if provided
    if query:
        users = users.filter(Q(nom__icontains=query) | Q(email__icontains=query))

    # Render the response
    context = {
        'users': users,
        'residences': residences,
        'query': query,
        'titlePage': _('Results for: "%s"') % query if query else _('Search Results'),
        'nom': user.nom,
        'date': timezone.now().strftime(_("%a %d %B %Y")),
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
    # Initialize as empty querysets
    syndics = Syndic.objects.none()
    supersyndics = SuperSyndic.objects.none()
    coproprietaires = Coproprietaire.objects.none()
    prestataires = Prestataire.objects.none()

    user = get_object_or_404(CustomUser, id=user_id)  # Get the user by ID

    # Fetch role-specific data
    if user.role == 'Superadmin':
        superadmin = get_object_or_404(Superadmin, user=user)
        profile = superadmin

    elif user.role == 'Syndic':
        syndic = get_object_or_404(Syndic, user=user)
        profile = syndic

        residences = Residence.objects.filter(syndic=syndic)
        # Retrieve the license associated with the syndic
        license = License.objects.filter(syndic=syndic).order_by('-date_debut').first()
        # Fetch associated coproprietaires and prestataires
        coproprietaires = Coproprietaire.objects.filter(syndic=syndic)
        prestataires = Prestataire.objects.filter(syndic=syndic)

        # Retrieve syndic and supersyndic associated with this coproprietaire
        syndics = Syndic.objects.filter(user=user)
        supersyndics = SuperSyndic.objects.filter(user=user)

    elif user.role == 'SuperSyndic':
        supersyndic = get_object_or_404(SuperSyndic, user=user)
        profile = supersyndic

        residences = Residence.objects.filter(supersyndic=supersyndic)
        license = License.objects.filter(supersyndic=supersyndic).order_by('-date_debut').first()
        # Fetch associated coproprietaires and prestataires
        coproprietaires = Coproprietaire.objects.filter(supersyndic=supersyndic)
        prestataires = Prestataire.objects.filter(supersyndic=supersyndic)

        # Retrieve syndic and supersyndic associated with this coproprietaire
        syndics = Syndic.objects.filter(user=user)
        supersyndics = SuperSyndic.objects.filter(user=user)

    elif user.role == 'Coproprietaire':
        coproprietaire = get_object_or_404(Coproprietaire, user=user)
        profile = coproprietaire
        
        # Fetch all residences associated with the coproprietaire
        residences = Residence.objects.filter(coproprietaire_residences=coproprietaire)

        # Retrieve syndic and supersyndic associated with this coproprietaire
        syndics = Syndic.objects.filter(syndic_coproprietaires=coproprietaire)
        supersyndics = SuperSyndic.objects.filter(supersyndic_coproprietaires=coproprietaire)

    elif user.role == 'Prestataire':
        prestataire = get_object_or_404(Prestataire, user=user)
        profile = prestataire
        
        # Fetch all residences associated with the prestataire
        residences = Residence.objects.filter(prestataire_residences=prestataire)

        # Retrieve syndic and supersyndic associated with this prestataire
        syndics = Syndic.objects.filter(syndic_prestataires=prestataire)
        supersyndics = SuperSyndic.objects.filter(supersyndic_prestataires=prestataire)

    # Calculate the total count
    total_count = coproprietaires.count() + prestataires.count()


    context = {
        'profile': profile,
        'nom': user.nom,
        'residences': residences,
        'syndics': syndics,
        'supersyndics': supersyndics,
        'superadmin': superadmin,
        'syndic': syndic,
        'supersyndic': supersyndic,
        'license': license,
        'coproprietaire': coproprietaire,
        'prestataire': prestataire,
        'coproprietaires': coproprietaires,
        'prestataires': prestataires,
        'total_count': total_count,
        'titlePage': _('Profile of %s') % user.nom,
        'date': timezone.now().strftime(_("%a %d %B %Y")),
    }

    html_template = loader.get_template('user-profile.html')
    return HttpResponse(html_template.render(context, request))
