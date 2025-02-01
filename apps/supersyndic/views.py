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

from core.utils import get_user_context, otp_required_for_supersyndic  # Import the helper function

from apps.authentication.models import CustomUser

from apps.superadmin.models import License

from apps.residence.models import Residence

from .models import SuperSyndic

from apps.coproprietaire.models import Coproprietaire

from apps.prestataire.models import Prestataire


# View for the Super User page, requiring 2FA status
@login_required(login_url="/login/")
@otp_required_for_supersyndic
@user_passes_test(lambda u: u.is_active and u.role in ['Superadmin', 'SuperSyndic'])
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
@user_passes_test(lambda u: u.is_active and u.role in ['Superadmin'])
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


# Delete SuperSyndic View
@user_passes_test(lambda u: u.is_active and u.role == 'Superadmin')
def delete_supersyndic(request, supersyndic_id):
    """
    Deletes a SuperSyndic and all related data (residences, coproprietaires, prestataires).
    """
    supersyndic = get_object_or_404(SuperSyndic, id=supersyndic_id)
    user = supersyndic.user  # Access the associated user account

    # Unlink the supersyndic from related coproprietaires
    supersyndic.supersyndic_coproprietaires.clear()  # Remove all coproprietaires from the many-to-many relationship

    # Clear many-to-many relationships for prestataires
    supersyndic.supersyndic_prestataires.clear()

    # Residences are many-to-many; ensure no deletion occurs (no explicit action is needed here)
    # Coproprietaires and Prestataires will still be linked to Residences.

    user.delete()  # Delete the CustomUser SuperSyndic
    messages.success(request, _('SuperSyndic "%s" has been deleted successfully.') % supersyndic.nom)
    return redirect('gestion-supersyndic')
