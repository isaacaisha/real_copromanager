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

from .models import Coproprietaire

from apps.prestataire.models import Prestataire


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
        'nom': coproprietaire.user.nom,
        'phone': coproprietaire.user.phone,
        'total_count': total_count,
        'date': timezone.now().strftime(_("%a %d %B %Y"))
    }

    html_template = loader.get_template('dashboard-coproprietaire.html')
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


# Delete Coproprietaire View
@user_passes_test(lambda u: u.is_active and u.role == 'Superadmin')
def delete_coproprietaire(request, coproprietaire_id):
    coproprietaire = get_object_or_404(Coproprietaire, user__id=coproprietaire_id)
    user = coproprietaire.user  # Access the linked CustomUser
    user.delete()  # Delete the CustomUser, which cascades the deletion to Coproprietaire
    messages.success(request, _('Coproprietaire "%s" has been deleted successfully.') % coproprietaire.nom)
    return redirect('gestion-coproprietaire')
