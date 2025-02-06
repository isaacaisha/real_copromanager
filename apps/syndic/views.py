# -*- encoding: utf-8 -*- apps/syndic/views.py

"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import gettext as _
from django.contrib import messages
from django.template import loader

from django.utils import timezone

from apps.authentication.models import CustomUser

from apps.superadmin.models import License

from apps.residence.models import Residence

from .models import Syndic

from apps.coproprietaire.models import Coproprietaire

from apps.prestataire.models import Prestataire

from apps.supersyndic.forms import SuperSyndicForm


# Syndic dashboard
@login_required(login_url="/login/")
@user_passes_test(lambda u: u.is_active and u.role in ['Superadmin', 'Syndic'])
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


@login_required(login_url="/login/")
@user_passes_test(lambda u: u.is_active and u.role in ['Superadmin'])
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


# Delete Syndic View
@user_passes_test(lambda u: u.is_active and u.role == 'Superadmin')
def delete_syndic(request, syndic_id):
    """
    Deletes a Syndic.
    """
    syndic = Syndic.objects.filter(user__id=syndic_id).first()
    if not syndic:
        print(f"No syndic found with id={syndic_id}")
        messages.warning(request, _('Syndic not found.'))
        return redirect('gestion-syndic')

    syndic.syndic_coproprietaires.clear()
    syndic.syndic_prestataires.clear()
    
    # Ensure the related user exists before trying to delete
    if syndic.user:
        try:
            syndic.user.delete()
        except Exception as e:
            print(f"Error deleting user: {e}")
    
    syndic.delete()
    messages.success(request, _('Syndic "%s" has been deleted successfully.') % syndic.nom)
    return redirect('gestion-syndic')
