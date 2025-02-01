# -*- encoding: utf-8 -*- apps/authentication/views.py

"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext as _
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.messages.views import SuccessMessageMixin

from django.urls import reverse_lazy
from django.utils import timezone

from apps.superadmin.models import Superadmin, License

from apps.residence.models import Residence

from apps.syndic.models import Syndic

from apps.supersyndic.models import SuperSyndic
from apps.supersyndic.forms import SuperSyndicForm

from apps.coproprietaire.models import Coproprietaire

from apps.prestataire.models import Prestataire

from .forms import SignUpForm, LoginForm, CustomPasswordResetConfirmForm

from apps.superadmin.forms import LicenseForm

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

    #exclude_residence = (role == 'Prestataire')  # Prestataire doesn't require a residence

    if request.method == "POST":
        form = SignUpForm(request.POST, logged_in_user=logged_in_user)
        license_form = LicenseForm(request.POST) if role == 'Syndic' else None

        if form.is_valid():
            user = form.save(commit=False)

            user.set_password(form.cleaned_data.get("password1"))

            creator = request.user
            if creator.role not in ['Superadmin', 'Syndic', 'SuperSyndic']:
                messages.warning(request, _("You do not have permission to register new users."))
                return redirect('register')

            user.save()

            if role == 'Coproprietaire':
                # Handle Coproprietaire registration
                return create_coproprietaire(request, user, form.cleaned_data.get('residence'), creator)

            elif role == 'Prestataire':
                # Handle Prestataire registration
                return create_prestataire(request, user, form.cleaned_data.get('residence'), creator)

            elif role == 'Syndic' and license_form and license_form.is_valid():
                # Handle Syndic registration with a license
                return create_syndic(request, user, license_form)

            else:
                messages.warning(request, _('Invalid role specified.'))
        else:
            messages.warning(request, _('Form is not valid.'))

    else:
        form = SignUpForm(initial={'role': role}, logged_in_user=logged_in_user) # , exclude_residence=exclude_residence)
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
        messages.warning(request, _('Residence is required for Coproprietaire.'))
        return redirect('register')

    if creator.role == 'Syndic':
        syndic = Syndic.objects.filter(user=creator).first()
        if not syndic:
            messages.warning(request, _('No associated Syndic found for the current user.'))
            return redirect('register')

        coproprietaire = Coproprietaire.objects.create(user=user)
        # Use add() instead of direct assignment
        coproprietaire.syndic.add(syndic)  
        coproprietaire.residence.add(residence)
        messages.success(request, _('Coproprietaire "%s" created successfully.') % coproprietaire.user.nom)
        return redirect('dashboard-coproprietaire', coproprietaire_id=user.id)

    elif creator.role == 'SuperSyndic':
        supersyndic = SuperSyndic.objects.filter(user=creator).first()
        if not supersyndic:
            messages.warning(request, _('No associated SuperSyndic found for the current user.'))
            return redirect('register')

        coproprietaire = Coproprietaire.objects.create(user=user)
        coproprietaire.supersyndic.add(supersyndic)  
        coproprietaire.residence.add(residence)
        messages.success(request, _('Coproprietaire "%s" created successfully.') % coproprietaire.user.nom)
        return redirect('dashboard-coproprietaire', coproprietaire_id=user.id)


def create_prestataire(request, user, residence, creator):
    """Helper function to create a Prestataire."""
    if creator.role == 'Syndic':
        syndic = Syndic.objects.filter(user=creator).first()
        if not syndic:
            messages.warning(request, _('No associated Syndic found for the current user.'))
            return redirect('register')

        prestataire = Prestataire.objects.create(user=user)
        # Use add() instead of direct assignment
        prestataire.syndic.add(syndic)  
        prestataire.residence.add(residence)
        messages.success(request, _('Prestataire "%s" created successfully.') % prestataire.user.nom)
        return redirect('dashboard-prestataire', prestataire_id=user.id)

    elif creator.role == 'SuperSyndic':
        supersyndic = SuperSyndic.objects.filter(user=creator).first()
        if not supersyndic:
            messages.warning(request, _('No associated SuperSyndic found for the current user.'))
            return redirect('register')

        prestataire = Prestataire.objects.create(user=user)
        prestataire.supersyndic.add(supersyndic)  
        prestataire.residence.add(residence)
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
                messages.warning(request, _('Invalid credentials.'))
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
        supersyndic_form = SuperSyndicForm(request.POST, instance=syndic.user, logged_in_user=request.user)  # Load the existing user instance
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
                        residence.syndic.remove(syndic)  # Remove the old syndic from ManyToMany
                        residence.supersyndic.add(supersyndic)  # Add the supersyndic to ManyToMany

                    # Transfer associated Coproprietaires
                    coproprietaires = Coproprietaire.objects.filter(syndic=syndic)
                    for coproprietaire in coproprietaires:
                        coproprietaire.syndic.remove(syndic)
                        coproprietaire.supersyndic.add(supersyndic) 

                    # Transfer associated Prestataires
                    prestataires = Prestataire.objects.filter(syndic=syndic)
                    for prestataire in prestataires:
                        prestataire.syndic.remove(syndic) 
                        prestataire.supersyndic.add(supersyndic) 

                    # Handle the license transfer
                    license = License.objects.filter(syndic=syndic).order_by('-date_debut').first()
                    if license:
                        license.syndic = None  # For ForeignKey
                        license.supersyndic = supersyndic  # Assign new supersyndic
                        license.save()

                    # Delete the old Syndic record
                    syndic.delete()

                    messages.success(request, _('Syndic successfully upgraded to Super Syndic.'))
                    return redirect('two_factor:setup')

            except Exception as e:
                messages.warning(request, f"An error occurred: {e}")
        else:
            messages.warning(request, _('Form is not valid.'))

    else:
        supersyndic_form = SuperSyndicForm(instance=syndic.user, logged_in_user=request.user)

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
