# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.messages.views import SuccessMessageMixin

from django.urls import reverse_lazy
from django.utils import timezone

from apps.authentication.models import CustomUser
from apps.home.models import License, Superadmin, Syndic, SuperSyndic, Coproprietaire, Prestataire
from .forms import LoginForm, SignUpForm, CustomPasswordResetConfirmForm, LicenseForm, SuperSyndicForm

# Create your views here.# auth_views.py

# View to handle role-based redirects
def redirect_based_on_role(request, user):
    """Redirects users based on their roles."""
    role_redirects = {
        'Superadmin': 'dashboard-superadmin',
        'Syndic': 'dashboard-syndic',
        'Coproprietaire': 'dashboard-coproprietaire',
        'Prestataire': 'dashboard-prestataire',
        'SuperSyndic': 'SuperSyndic',
    }

    if user.role == 'Syndic':
        syndic, created = Syndic.objects.get_or_create(user=user)  # Ensure syndic instance exists
        return redirect('dashboard-syndic', syndic_id=syndic.id)  # Redirect with syndic_id

    elif user.role == 'Coproprietaire':
        coproprietaire, created = Coproprietaire.objects.get_or_create(user=user)
        return redirect('dashboard-coproprietaire', coproprietaire_id=coproprietaire.id)

    elif user.role == 'Prestataire':
        prestataire, created = Prestataire.objects.get_or_create(user=user)
        return redirect('dashboard-prestataire', prestataire_id=prestataire.id)

    elif user.role == 'SuperSyndic':
        super_syndic, created = SuperSyndic.objects.get_or_create(user=user)
        return redirect('dashboard-super-syndic', super_syndic_id=super_syndic.id)


    # For other roles, simply redirect to the appropriate dashboard
    return redirect(role_redirects.get(user.role, 'home'))


#@user_passes_test(lambda u: u.is_active and u.role == 'Superadmin')
def register_user(request):
    msg = None
    success = False

    if request.method == "POST":
        form = SignUpForm(request.POST)
        license_form = LicenseForm(request.POST)
        
        if form.is_valid():

            # return redirect("/login/")
            user = form.save(commit=False)
            user.set_password(form.cleaned_data.get("password1"))
            user.save()

            # Handle role-based logic as in your previous code
            if user.role == 'Superadmin':
                Superadmin.objects.create(user=user)
                messages.success(request, 'Superadmin created successfully.')
                msg = 'Superadmin-User created - please <a href="/login">login</a>.'
                success = True
                return redirect('login')

            elif user.role == 'Syndic':
                # Create a Syndic and associate the license
                syndic = Syndic.objects.create(user=user, nom=user.nom, email=user.email)
                # Create a License instance linked to the newly created Syndic
                license_form = LicenseForm(request.POST)
                if license_form.is_valid():
                    license = license_form.save(commit=False)
                    license.syndic = syndic  # Link license to the Syndic
                    license.save()

                    # Assign the license to the syndic and save
                    syndic.license = license
                    syndic.save()
                    
                    messages.success(request, 'Syndic created successfully.')
                    return redirect('dashboard-superadmin')
                else:
                    print("License form is not valid:", license_form.errors)
                    messages.error(request, 'License form is not valid.')
                    syndic.delete()  # Rollback syndic creation if license creation fails
                    return redirect('register')

            elif user.role == 'Coproprietaire':
                # Assign the user to an existing syndic (if available)
                syndic = Syndic.objects.first()
                if syndic:
                    Coproprietaire.objects.create(user=user, syndic=syndic)
                    messages.success(request, 'Coproprietaire created successfully.')
                else:
                    messages.error(request, 'No syndic available to assign to Coproprietaire.')
                msg = 'Coproprietaire-User created - please <a href="/login">login</a>.'
                success = True
                return redirect('dashboard-superadmin')

            elif user.role == 'Prestataire':
                # Assign the user to an existing syndic (if available)
                syndic = Syndic.objects.first()
                if syndic:
                    Prestataire.objects.create(user=user, syndic=syndic)
                    messages.success(request, 'Prestataire created successfully.')
                else:
                    messages.error(request, 'No syndic available to assign to Prestataire.')
                msg = 'Prestataire-User created - please <a href="/login">login</a>.'
                success = True
                return redirect('dashboard-superadmin')
        else:
            msg = 'Form is not valid'

    else:
        form = SignUpForm()
        license_form = LicenseForm()

    context = {
        'form': form,
        'license_form': license_form,
        'msg': msg,
        'success': success,
        'titlePage': 'Incriptions',
        'date': timezone.now().strftime("%a %d %B %Y")
    }

    return render(request, "accounts/register.html", context)


def login_view(request):
    form = LoginForm(request.POST or None)
    msg = None

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
                msg = 'Invalid credentials.'
        else:
            msg = 'Form is not valid. Please check the details.'
        
    context = {
        'form': form,
        'msg': msg,
        'titlePage': 'Connexion/Login',
        'date': timezone.now().strftime("%a %d %B %Y")
    }

    return render(request, "accounts/login.html", context)


# View for user logout
def logout_view(request):
    logout(request)
    return redirect('home')


class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    success_message = "Un email vous à été envoyez avec les instruction à suivre, " \
                      "Si un compte existe sur l'Email fournis, Vous allez rapidement recevoir un message." \
                      " Si vous ne recevez pas d'email, " \
                      "s'il vous plaît assurez vous d'avoir introduit l'addresse avec laquelle vous ête enregistrez, " \
                      "et vérifiez votre dossier spam."
    success_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titlePage'] = 'Réinitialisation du Mot de Passe'
        context['date'] = timezone.now().strftime("%a %d %B %Y")
        return context

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    form_class = CustomPasswordResetConfirmForm
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titlePage'] = 'Confirmation du nouveau Mot de Passe'
        context['date'] = timezone.now().strftime("%a %d %B %Y")
        return context

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titlePage'] = 'Réinitialisation Accompli'
        context['date'] = timezone.now().strftime("%a %d %B %Y")
        return context
    

# Delete Syndic View
@user_passes_test(lambda u: u.is_active and u.role == 'Superadmin')
def delete_syndic(request, syndic_id):
    syndic = get_object_or_404(CustomUser, id=syndic_id, role='Syndic')
    syndic.delete()
    messages.success(request, f'Syndic {syndic.nom} has been deleted.')
    return redirect('gestion-syndic')

# Delete SuperSyndic View
@user_passes_test(lambda u: u.is_active and u.role == 'Superadmin')
def delete_super_syndic(request, super_syndic_id):
    super_syndic = get_object_or_404(CustomUser, id=super_syndic_id)
    super_syndic.delete()
    messages.success(request, f'SuperSyndic {super_syndic.nom} has been deleted.')
    return redirect('/gestion-super-syndic')

# Delete Coproprietaire View
@user_passes_test(lambda u: u.is_active and u.role == 'Superadmin')
def delete_coproprietaire(request, coproprietaire_id):
    coproprietaire = get_object_or_404(Coproprietaire, user__id=coproprietaire_id)
    user = coproprietaire.user  # Access the linked CustomUser
    user.delete()  # Delete the CustomUser, which cascades the deletion to Coproprietaire
    messages.success(request, f'Coproprietaire {user.nom} has been deleted.')
    return redirect('/gestion-coproprietaire')

# Delete Prestataire View
@user_passes_test(lambda u: u.is_active and u.role == 'Superadmin')
def delete_prestataire(request, prestataire_id):
    prestataire = get_object_or_404(Prestataire, user__id=prestataire_id)
    user = prestataire.user  # Access the linked CustomUser
    user.delete()  # Delete the CustomUser, which cascades the deletion to Prestataire
    messages.success(request, f'Prestataire {user.nom} has been deleted.')
    return redirect('/gestion-prestataire')


# View for the register Super Syndic, requiring 2FAfrom django.db import transaction
@login_required
def register_super_syndic(request, syndic_id):
    titlePage = 'Register Super Syndic'
    super_syndic_form = SuperSyndicForm(request.POST or None)
    syndic = get_object_or_404(Syndic, id=syndic_id)
    super_syndic = None
    #super_syndic, created = SuperSyndic.objects.get_or_create(user=request.user)
    #super_syndic = Syndic.objects.create(user=user, nom=user.nom, email=user.email)

    if request.method == "POST":
        super_syndic_form = SuperSyndicForm(request.POST, instance=syndic.user)  # Load the existing user instance
        if super_syndic_form.is_valid():
            try:
                with transaction.atomic():
                    # Update the user's role to SuperSyndic
                    user = super_syndic_form.save(commit=False)
                    user.role = 'SuperSyndic'
                    user.save()

                    # Create or get a SuperSyndic instance for this user
                    super_syndic, created = SuperSyndic.objects.get_or_create(user=user)

                    # Handle the license transfer
                    # Assuming that a syndic can have multiple licenses, we fetch the latest one
                    license = License.objects.filter(syndic=syndic).order_by('-date_debut').first()
                    if license:
                        # Assign the license to the SuperSyndic (if needed)
                        license.super_syndic = super_syndic
                        license.syndic = None  # Remove the license from the old syndic
                        license.save()

                    messages.success(request, 'User successfully upgraded to Super Syndic!')
                    return redirect('two_factor:setup')  # Or your desired next step

            except Exception as e:
                messages.error(request, f"An error occurred: {e}")
        else:
            messages.error(request, 'Form is not valid.')
    else:
        # Pre-fill the form with the current user's data
        super_syndic_form = SuperSyndicForm(instance=syndic.user)

    context = {
        'titlePage': titlePage,
        'syndic': syndic,
        'super_syndic': super_syndic,
        'super_syndic_form': super_syndic_form,
        'date': timezone.now().strftime("%a %d %B %Y"),
        'message': 'Upgrade your profile to Super Syndic!',
    }
    return render(request, 'accounts/register-login-super-syndic.html', context)


# View for the login VIP page, requiring 2FA
@login_required
def login_super_syndic(request, super_syndic_id):
    titlePage = 'Login'

    # Fetch the current logged-in user's syndic profile
    #syndic = Syndic.objects.get(id=syndic_id)
    #syndic = get_object_or_404(Syndic, id=syndic_id)
    try:
        #super_syndic = SuperSyndic.objects.get(id=super_syndic_id)
        #super_syndic = get_object_or_404(SuperSyndic, id=super_syndic_id)
        super_syndic, created = SuperSyndic.objects.get_or_create(user=request.user)
    except SuperSyndic.DoesNotExist:
        super_syndic = None

    context = {
        'titlePage': titlePage,
        'super_syndic': super_syndic,
        'date': timezone.now().strftime("%a %d %B %Y"),
        'message': 'Welcome to the VIP User Page!',
    }
    return render(request, 'accounts/register-login-super-syndic.html', context)
    
    #return redirect('two_factor:login')
