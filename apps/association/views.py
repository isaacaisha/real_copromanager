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

from apps.supersyndic.models import SuperSyndic

from apps.coproprietaire.models import Coproprietaire

from apps.prestataire.models import Prestataire

from .forms import (
    AssignSyndicForm, RemoveSyndicForm,
    AssociateToResidenceForm, AssociateToSyndicateForm
    )


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
@user_passes_test(lambda u: u.is_active and u.role in ['Superadmin'])
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
        #syndics = Syndic.objects.filter(syndic_residences__in=residences).exclude(pk=syndic_profile.pk).distinct()
        syndics = Syndic.objects.filter(syndic_residences__in=residences).distinct()
        
        # Retrieve the associated SuperSyndic(s) for the residences
        supersyndics = SuperSyndic.objects.filter(supersyndic_residences__in=residences).distinct()

    elif request.user.role == 'SuperSyndic' and hasattr(request.user, 'supersyndic_profile'):
        supersyndic_profile = request.user.supersyndic_profile
        residences = Residence.objects.filter(supersyndic=supersyndic_profile)
        
        # Only include coproprietaires and prestataires linked to these supersyndic_profile
        coproprietaires = Coproprietaire.objects.filter(supersyndic=supersyndic_profile)
        prestataires = Prestataire.objects.filter(supersyndic=supersyndic_profile)

        # Syndics assigned to residences under this SuperSyndic
        syndics = Syndic.objects.filter(syndic_residences__in=residences).distinct()

        # SuperSyndics associated with residences under the same management
        #supersyndics = SuperSyndic.objects.filter(supersyndic_residences__in=residences).exclude(pk=supersyndic_profile.pk).distinct()
        # Retrieve the associated SuperSyndic(s) for the residences
        supersyndics = SuperSyndic.objects.filter(supersyndic_residences__in=residences).distinct()

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
            Q(coproprietaire_profile__syndic__in=syndic_queryset) |
            Q(prestataire_profile__syndic__in=syndic_queryset) 
        ).distinct()
    
    if not supersyndic_queryset:
        presta_residence_users = CustomUser.objects.none()
    else:
        presta_residence_users = CustomUser.objects.filter(
            Q(coproprietaire_profile__supersyndic__in=supersyndic_queryset) |
            Q(prestataire_profile__supersyndic__in=supersyndic_queryset)
        ).distinct()

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
