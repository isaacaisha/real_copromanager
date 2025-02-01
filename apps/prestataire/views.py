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

from .models import Prestataire

from apps.coproprietaire.models import Coproprietaire


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
        'nom': prestataire.user.nom,
        'phone': prestataire.user.phone,
        'total_count_presta': total_count_presta,
        'date': timezone.now().strftime(_("%a %d %B %Y"))
    }

    html_template = loader.get_template('dashboard-prestataire.html')
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


# Delete Prestataire View
@user_passes_test(lambda u: u.is_active and u.role == 'Superadmin')
def delete_prestataire(request, prestataire_id):
    prestataire = get_object_or_404(Prestataire, user__id=prestataire_id)
    user = prestataire.user  # Access the linked CustomUser
    user.delete()  # Delete the CustomUser, which cascades the deletion to Prestataire
    messages.success(request, _('Prestataire "%s" has been deleted successfully.') % prestataire.nom)
    return redirect('gestion-prestataire')
