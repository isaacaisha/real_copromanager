# -*- encoding: utf-8 -*- apps/authentication/views.py

"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext as _
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.messages.views import SuccessMessageMixin

from django.urls import reverse_lazy
from django.utils import timezone

from apps.authentication.models import CustomUser
from .forms import LoginForm, SignUpForm, CustomPasswordResetConfirmForm, SuperSyndicForm, SyndicForm

from apps.dashboard.models import License, Residence, Superadmin, Syndic, SuperSyndic, Coproprietaire, Prestataire
from apps.dashboard.forms import LicenseForm

# Create your views here.# auth_views.py

# View to handle role-based redirects
def redirect_based_on_role(request, user):
    """Redirects users based on their roles."""
    role_redirects = {
        'Superadmin': 'dashboard-superadmin',
        'Syndic': 'dashboard-syndic',
        'Coproprietaire': 'dashboard-coproprietaire',
        'Prestataire': 'dashboard-prestataire',
        'SuperSyndic': 'dashboard-supersyndic',
    }

    if user.role == 'Superadmin':
        superadmin, created = Superadmin.objects.get_or_create(user=user)  # Ensure superadmin instance exists
        return redirect('dashboard-superadmin', superadmin_id=superadmin.id)  # Redirect with superadmin_id

    elif user.role == 'Syndic':
        syndic, created = Syndic.objects.get_or_create(user=user)  # Ensure syndic instance exists
        return redirect('dashboard-syndic', syndic_id=syndic.id)  # Redirect with syndic_id

    elif user.role == 'Coproprietaire':
        coproprietaire, created = Coproprietaire.objects.get_or_create(user=user)
        return redirect('dashboard-coproprietaire', coproprietaire_id=coproprietaire.id)

    elif user.role == 'Prestataire':
        prestataire, created = Prestataire.objects.get_or_create(user=user)
        return redirect('dashboard-prestataire', prestataire_id=prestataire.id)

    elif user.role == 'SuperSyndic':
        supersyndic, created = SuperSyndic.objects.get_or_create(user=user)
        return redirect('dashboard-supersyndic', supersyndic_id=supersyndic.id)


    # For other roles, simply redirect to the appropriate dashboard
    return redirect(role_redirects.get(user.role, 'home'))


@login_required(login_url="/login/")
@user_passes_test(lambda u: u.is_active and u.role in ['Superadmin', 'Syndic', 'SuperSyndic'])
def register_user(request):
    role = request.GET.get('role')  # Extract the role from the URL query parameter
    logged_in_user = request.user

    exclude_residence = (role == 'Prestataire')  # Prestataire doesn't require a residence

    if request.method == "POST":
        form = SignUpForm(request.POST, logged_in_user=logged_in_user)
        license_form = LicenseForm(request.POST) if role == 'Syndic' else None

        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data.get("password1"))

            creator = request.user
            if creator.role not in ['Superadmin', 'Syndic', 'SuperSyndic']:
                messages.error(request, _("You do not have permission to register new users."))
                return redirect('register')

            user.save()

            if role == 'Coproprietaire':
                # Handle Coproprietaire registration
                return create_coproprietaire(request, user, form.cleaned_data.get('residence'), creator)

            elif role == 'Prestataire':
                # Handle Prestataire registration
                return create_prestataire(request, user, creator)

            elif role == 'Syndic' and license_form and license_form.is_valid():
                # Handle Syndic registration with a license
                return create_syndic(request, user, license_form)

            elif role == 'Superadmin':
                # Handle Superadmin registration
                Superadmin.objects.create(user=user)
                messages.success(request, _('Superadmin created successfully.'))
                return redirect('dashboard-superadmin', superadmin_id=user.id)

            else:
                messages.error(request, _('Invalid role specified.'))
        else:
            messages.error(request, _('Form is not valid.'))

    else:
        form = SignUpForm(initial={'role': role}, logged_in_user=logged_in_user, exclude_residence=exclude_residence)
        license_form = LicenseForm() if role == 'Syndic' else None

    context = {
        'form': form,
        'license_form': license_form,
        'titlePage': _('Registration'),
        'date': timezone.now().strftime(_("%a %d %B %Y")),
    }
    return render(request, "accounts/register.html", context)


def create_coproprietaire(request, user, residence, creator):
    """Helper function to create a Coproprietaire."""
    if not residence:
        messages.error(request, _('Residence is required for Coproprietaire.'))
        return redirect('register')

    if creator.role == 'Syndic':
        syndic = Syndic.objects.filter(user=creator).first()
        if not syndic:
            messages.error(request, _('No associated Syndic found for the current user.'))
            return redirect('register')

        coproprietaire = Coproprietaire.objects.create(user=user, syndic=syndic)
        coproprietaire.residence.add(residence)
        messages.success(request, _('Coproprietaire "%s" created successfully.') % coproprietaire.user.nom)
        return redirect('dashboard-coproprietaire', coproprietaire_id=user.id)

    elif creator.role == 'SuperSyndic':
        supersyndic = SuperSyndic.objects.filter(user=creator).first()
        if not supersyndic:
            messages.error(request, _('No associated SuperSyndic found for the current user.'))
            return redirect('register')

        coproprietaire = Coproprietaire.objects.create(user=user, supersyndic=supersyndic)
        coproprietaire.residence.add(residence)
        messages.success(request, _('Coproprietaire "%s" created successfully.') % coproprietaire.user.nom)
        return redirect('dashboard-coproprietaire', coproprietaire_id=user.id)


def create_prestataire(request, user, creator):
    """Helper function to create a Prestataire."""
    if creator.role == 'Syndic':
        syndic = Syndic.objects.filter(user=creator).first()
        if not syndic:
            messages.error(request, _('No associated Syndic found for the current user.'))
            return redirect('register')

        prestataire = Prestataire.objects.create(user=user, syndic=syndic)
        messages.success(request, _('Prestataire "%s" created successfully.') % prestataire.user.nom)
        return redirect('dashboard-prestataire', prestataire_id=user.id)

    elif creator.role == 'SuperSyndic':
        supersyndic = SuperSyndic.objects.filter(user=creator).first()
        if not supersyndic:
            messages.error(request, _('No associated SuperSyndic found for the current user.'))
            return redirect('register')

        prestataire = Prestataire.objects.create(user=user, supersyndic=supersyndic)
        messages.success(request, _('Prestataire "%s" created successfully.') % prestataire.user.nom)
        return redirect('dashboard-prestataire', prestataire_id=user.id)


def create_syndic(request, user, license_form):
    """Helper function to create a Syndic with a license."""
    syndic = Syndic.objects.create(user=user, nom=user.nom, email=user.email)
    license = license_form.save(commit=False)
    license.syndic = syndic
    license.save()

    syndic.license = license
    syndic.save()

    messages.success(request, _('Syndic "%s" created successfully.') % syndic.nom)
    return redirect('dashboard-syndic', syndic_id=user.id)


def login_view(request):
    form = LoginForm(request.POST or None)

    if request.method == "POST":

        if form.is_valid():
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            user = authenticate(email=email, password=password)

            if user is not None:
                login(request, user)
                #return redirect("/")
                return redirect_based_on_role(request, user)
            else:
                messages.error(request, _('Invalid credentials.'))
        else:
            messages.error(request, _('Form is not valid. Please check the details.'))
        
    context = {
        'form': form,
        'titlePage': _('Login'),
        'date': timezone.now().strftime("%a %d %B %Y")
    }
    context['date'] = _(context['date']) 

    return render(request, "accounts/login.html", context)


# View for the register Super Syndic, requiring 2FAfrom django.db import transaction
@login_required
@user_passes_test(lambda u: u.is_active and u.role == 'Syndic')
def register_supersyndic(request, syndic_id):
    titlePage = _('Register Super Syndic')
    supersyndic_form = SuperSyndicForm(request.POST or None)
    syndic = get_object_or_404(Syndic, id=syndic_id)

    if request.method == "POST":
        supersyndic_form = SuperSyndicForm(request.POST, instance=syndic.user)  # Load the existing user instance
        if supersyndic_form.is_valid():
            try:
                with transaction.atomic():
                    # Update the user's role to SuperSyndic
                    user = supersyndic_form.save(commit=False)
                    user.role = 'SuperSyndic'
                    user.save()

                    # Create or get a SuperSyndic instance for this user
                    supersyndic, created = SuperSyndic.objects.get_or_create(user=user)

                    # Transfer residences to the SuperSyndic
                    residences = Residence.objects.filter(syndic=syndic)
                    for residence in residences:
                        residence.syndic = None
                        residence.supersyndic = supersyndic
                        residence.save()

                    # Transfer associated Coproprietaires
                    coproprietaires = Coproprietaire.objects.filter(syndic=syndic)
                    for coproprietaire in coproprietaires:
                        coproprietaire.syndic = None
                        coproprietaire.supersyndic = supersyndic
                        coproprietaire.save()

                    # Transfer associated Prestataires
                    prestataires = Prestataire.objects.filter(syndic=syndic)
                    for prestataire in prestataires:
                        prestataire.syndic = None
                        prestataire.supersyndic = supersyndic
                        prestataire.save()

                    # Handle the license transfer
                    license = License.objects.filter(syndic=syndic).order_by('-date_debut').first()
                    if license:
                        license.supersyndic = supersyndic
                        license.syndic = None
                        license.save()

                    # Delete the old Syndic record
                    syndic.delete()

                    messages.success(request, _('Syndic successfully upgraded to Super Syndic.'))
                    return redirect('two_factor:setup')

            except Exception as e:
                messages.error(request, f"An error occurred: {e}")
        else:
            messages.error(request, _('Form is not valid.'))

    else:
        supersyndic_form = SuperSyndicForm(instance=syndic.user)

    context = {
        'titlePage': titlePage,
        'nom': request.user.nom,
        'syndic': syndic,
        'supersyndic_form': supersyndic_form,
        'date': timezone.now().strftime(_("%a %d %B %Y")),
    }
    return render(request, 'accounts/register-login-supersyndic.html', context)


# View for the login VIP page, requiring 2FA
@login_required
@user_passes_test(lambda u: u.is_active and u.role == 'Supersyndic')
def login_supersyndic(request, supersyndic_id):
    titlePage = _('Login Super Syndic')

    try:
        supersyndic = get_object_or_404(SuperSyndic, id=supersyndic_id)
    except SuperSyndic.DoesNotExist:
        supersyndic = None

    context = {
        'titlePage': titlePage,
        'supersyndic': supersyndic,
        'date': timezone.now().strftime(_("%a %d %B %Y")),
    }
    return render(request, 'accounts/register-login-supersyndic.html', context)


# View for user logout
def logout_view(request):
    logout(request)
    return redirect('home')


class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    success_message = _(
        "An email has been sent with instructions to reset your password. "
        "If no email arrives, please ensure you've entered the correct email address "
        "registered with your account and check your spam folder."
    )
    success_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titlePage'] = _('Password Reset')
        context['date'] = timezone.now().strftime(_("%a %d %B %Y"))
        return context

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    form_class = CustomPasswordResetConfirmForm
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titlePage'] = _('New Password Confirmation')
        context['date'] = timezone.now().strftime(_("%a %d %B %Y"))
        return context

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titlePage'] = _('Password Reset Complete')
        context['date'] = timezone.now().strftime(_("%a %d %B %Y"))
        return context


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
                            residence.supersyndic = supersyndic
                            residence.save()

                        # Transfer associated Coproprietaires and Prestataires
                        coproprietaires = Coproprietaire.objects.filter(syndic=None, supersyndic=None)
                        prestataires = Prestataire.objects.filter(syndic=None, supersyndic=None)

                        for coproprietaire in coproprietaires:
                            coproprietaire.syndic = supersyndic
                            coproprietaire.save()

                        for prestataire in prestataires:
                            prestataire.syndic = supersyndic
                            prestataire.save()

                        messages.success(request, _("Profile '%s' updated successfully") % profile.nom)
                        return redirect('dashboard-supersyndic', supersyndic_id=user_id)

                except Exception as e:
                    messages.error(request, f"An error occurred: {e}")
            else:
                messages.error(request, _("Form is not valid."))

        elif profile.role == "Syndic":
            # Use SyndicForm for Syndic role
            syndic_form = SyndicForm(request.POST, instance=profile)
            if syndic_form.is_valid():
                try:
                    with transaction.atomic():
                        syndic_form.save()
                        messages.success(request, _("Profile '%s' updated successfully") % profile.nom)
                        return redirect('dashboard-syndic', syndic_id=user_id)
                except Exception as e:
                    messages.error(request, f"An error occurred: {e}")
            else:
                messages.error(request, _("Please correct the errors in the form."))

        else:
            form = SignUpForm(request.POST, instance=profile, exclude_residence=True)
            if form.is_valid():
                form.save()
                messages.success(request, _("Profile '%s' updated successfully") % profile.nom)
                return redirect('home')
            else:
                messages.error(request, _("There were errors in the form. Please correct them."))

    else:
        # Prepopulate forms for GET requests
        if profile.role == "SuperSyndic":
            supersyndic_form = SuperSyndicForm(instance=profile)
        elif profile.role == "Syndic":
            syndic_form = SyndicForm(instance=profile)
        else:
            form = SignUpForm(instance=profile, exclude_residence=True)

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
    return render(request, "accounts/update_profile.html", context)


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


# Delete Syndic View
@user_passes_test(lambda u: u.is_active and u.role == 'Superadmin')
def delete_syndic(request, syndic_id):
    """
    Deletes a Syndic and all related data (residences, coproprietaires, prestataires).
    """
    syndic = get_object_or_404(Syndic, user__id=syndic_id)
    # Delete related residences
    syndic.syndic_residences.all().delete()
    # Delete related coproprietaires
    syndic.syndic_coproprietaires.all().delete()
    # Delete related prestataires
    Prestataire.objects.filter(syndic=syndic).delete()
    # Delete the syndic
    syndic = get_object_or_404(CustomUser, id=syndic_id, role='Syndic')
    syndic.delete()
    messages.success(request, _('Syndic "%s" and all their related data have been deleted.') % syndic.nom)
    return redirect('gestion-syndic')


# Delete SuperSyndic View
@user_passes_test(lambda u: u.is_active and u.role == 'Superadmin')
def delete_supersyndic(request, supersyndic_id):
    """
    Deletes a SuperSyndic and all related data (residences, coproprietaires, prestataires).
    """
    supersyndic = get_object_or_404(SuperSyndic, user__id=supersyndic_id)
    # Delete related residences
    supersyndic.supersyndic_residences.all().delete()
    # Delete related coproprietaires
    supersyndic.supersyndic_coproprietaires.all().delete()
    # Delete related prestataires
    Prestataire.objects.filter(supersyndic=supersyndic).delete()
    # Delete the supersyndic
    supersyndic = get_object_or_404(CustomUser, id=supersyndic_id, role='SuperSyndic')
    supersyndic.delete()
    messages.success(request, _('SuperSyndic "%s" and all their related data have been deleted.') % supersyndic.nom)
    return redirect('gestion-supersyndic')


# Delete Coproprietaire View
@user_passes_test(lambda u: u.is_active and u.role == 'Superadmin')
def delete_coproprietaire(request, coproprietaire_id):
    coproprietaire = get_object_or_404(Coproprietaire, user__id=coproprietaire_id)
    user = coproprietaire.user  # Access the linked CustomUser
    user.delete()  # Delete the CustomUser, which cascades the deletion to Coproprietaire
    messages.success(request, _('Coproprietaire "%s" has been deleted.') % user.nom)
    return redirect('gestion-coproprietaire')


# Delete Prestataire View
@user_passes_test(lambda u: u.is_active and u.role == 'Superadmin')
def delete_prestataire(request, prestataire_id):
    prestataire = get_object_or_404(Prestataire, user__id=prestataire_id)
    user = prestataire.user  # Access the linked CustomUser
    user.delete()  # Delete the CustomUser, which cascades the deletion to Prestataire
    messages.success(request, _('Prestataire "%s" has been deleted.') % user.nom)
    return redirect('gestion-prestataire')
