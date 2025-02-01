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

from apps.residence.models import Residence

from apps.syndic.models import Syndic

from apps.coproprietaire.models import Coproprietaire

from apps.prestataire.models import Prestataire

from .forms import ResidenceForm


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


# Delete Syndic View
@user_passes_test(lambda u: u.is_active and (u.role == 'Superadmin' or u.role in ['Syndic', 'SuperSyndic']))
def delete_residence(request, residence_id):
    # Fetch the residence or return a 404 if not found
    residence = get_object_or_404(Residence, id=residence_id)
    # Delete the residence
    residence_name = residence.nom  # Save the name for the success message
    residence.delete()
    # Notify the user and redirect to the residence management page
    messages.success(request, _('Residence "%(nom)s" has been deleted.') % {'nom': residence_name})
    return redirect('gestion-residence')
