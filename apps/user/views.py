# -*- encoding: utf-8 -*- apps/dashboard/views.py

"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import gettext as _
from django.contrib import messages
from django.template import loader

from django.db.models import Q  # Import Q for complex queries

from django.utils import timezone

from apps.authentication.models import CustomUser

from apps.superadmin.models import Superadmin, License

from apps.residence.models import Residence

from apps.syndic.models import Syndic

from apps.supersyndic.models import SuperSyndic

from apps.coproprietaire.models import Coproprietaire

from apps.prestataire.models import Prestataire

from apps.authentication.forms import SignUpForm
from apps.syndic.forms import SyndicForm
from apps.supersyndic.forms import SuperSyndicForm


@login_required(login_url="/login/")
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


@login_required
def update_profile(request, user_id=None):
    """
    View to update a user's profile.
    - Superadmin can update any profile if `user_id` is provided.
    - SuperSyndic updates use `supersyndic_form`.
    - Syndic updates use `syndic_form`.
    - Superadmin updates or creates profiles using `form`.
    """

    form = None
    syndic_form = None
    supersyndic_form = None
    
    # Determine the user to update based on the role
    if request.user.role == "Superadmin" and user_id:
        # Superadmin is updating another user's profile
        profile = get_object_or_404(CustomUser, id=user_id)
    else:
        # Default to updating the current user's profile
        profile = request.user

    # Handle form submission
    if request.method == "POST":
        if request.user.role == "Superadmin" and profile.role == "SuperSyndic" or request.user.role == "SuperSyndic" and profile.role == 'SuperSyndic':
            # Use the SuperSyndic form for SuperSyndic profiles
            supersyndic_form = SuperSyndicForm(request.POST, instance=profile)
            if supersyndic_form.is_valid():
                try:
                    with transaction.atomic():
                        user = supersyndic_form.save(commit=False)
                        # Preserve current role and upgrade to 'SuperSyndic'
                        user.role = 'SuperSyndic'
                        user.save()

                        # Handle the license transfer
                        supersyndic = get_object_or_404(SuperSyndic, user=profile)
                        license = License.objects.filter(supersyndic=supersyndic).order_by('-date_debut').first()
                        if license:
                            license.supersyndic = supersyndic  # Link license to the updated SuperSyndic
                            license.syndic = None  # Remove the license from the old syndic (if applicable)
                            license.save()

                        # Transfer residences to the SuperSyndic
                        residences = Residence.objects.filter(syndic=None, supersyndic=None)
                        for residence in residences:
                            residence.supersyndic.add(supersyndic)

                        # Transfer associated Coproprietaires and Prestataires
                        coproprietaires = Coproprietaire.objects.filter(syndic=None, supersyndic=None)
                        prestataires = Prestataire.objects.filter(syndic=None, supersyndic=None)

                        for coproprietaire in coproprietaires:
                            coproprietaire.supersyndic.add(supersyndic)

                        for prestataire in prestataires:
                            prestataire.supersyndic.add(supersyndic)

                        messages.success(request, _("Profile '%s' updated successfully") % profile.nom)
                        return redirect('dashboard-supersyndic', supersyndic_id=user_id)

                except Exception as e:
                    messages.warning(request, f"An error occurred: {e}")
            else:
                messages.warning(request, _("Form is not valid."))

        elif profile.role == "Syndic":
            # Use SyndicForm for Syndic role
            syndic_form = SyndicForm(request.POST, instance=profile, logged_in_user=request.user)
            if syndic_form.is_valid():
                try:
                    with transaction.atomic():
                        syndic_form.save()
                        messages.success(request, _("Profile '%s' updated successfully") % profile.nom)
                        return redirect('dashboard-syndic', syndic_id=user_id)
                except Exception as e:
                    messages.warning(request, f"An error occurred: {e}")
            else:
                messages.warning(request, _("Please correct the errors in the form."))

        else:
            form = SignUpForm(request.POST, instance=profile, exclude_residence=True, logged_in_user=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, _("Profile '%s' updated successfully") % profile.nom)
                return redirect('home')
            else:
                messages.warning(request, _("There were errors in the form. Please correct them."))

    else:
        # Prepopulate forms for GET requests
        if profile.role == "SuperSyndic":
            supersyndic_form = SuperSyndicForm(instance=profile, logged_in_user=request.user)
        elif profile.role == "Syndic":
            syndic_form = SyndicForm(instance=profile, logged_in_user=request.user)
        else:
            form = SignUpForm(instance=profile, exclude_residence=True, logged_in_user=request.user)

    context = {
        'form': form,
        'syndic_form': syndic_form,
        'supersyndic_form': supersyndic_form,
        'profile': profile,
        'id': profile.id if profile else None,
        'titlePage': _("Update '%s' Profile ") % profile.nom,
        'nom': request.user.nom,
        'date': timezone.now().strftime(_("%a %d %B %Y")),
    }

    html_template = loader.get_template('update_profile.html')
    return HttpResponse(html_template.render(context, request))
