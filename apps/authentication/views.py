# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

from apps.authentication.models import CustomUser
from apps.home.models import Coproprietaire, Prestataire, Superadmin, Syndic
from .forms import LoginForm, SignUpForm, LicenseForm
from django.utils import timezone

# Create your views here.# auth_views.py

# View to handle role-based redirects
def redirect_based_on_role(request, user):
    """Redirects users based on their roles."""
    role_redirects = {
        'Superadmin': 'dashboard-superadmin',
        'Syndic': 'dashboard-syndic',
        'Coproprietaire': 'dashboard-coproprietaire',
        'Prestataire': 'dashboard-prestataire',
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


    # For other roles, simply redirect to the appropriate dashboard
    return redirect(role_redirects.get(user.role, 'home'))


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
        'date': timezone.now().strftime("%a %d %B %Y")
    }

    return render(request, "accounts/login.html", context)


# View for user logout
def logout_view(request):
    logout(request)
    return redirect('home')


#@user_passes_test(lambda u: u.is_active and u.role == 'Superadmin')
def register_user(request):
    msg = None
    success = False

    if request.method == "POST":
        form = SignUpForm(request.POST)
        license_form = LicenseForm(request.POST)
        
        if form.is_valid():
            #form.save()
            #username = form.cleaned_data.get("username")
            #raw_password = form.cleaned_data.get("password1")
            #user = authenticate(username=username, password=raw_password)

            #msg = 'User created - please <a href="/login">login</a>.'
            #success = True

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
                    
                    messages.success(request, 'Syndic created successfully, Edit the License.')
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


# Delete Syndic View
@user_passes_test(lambda u: u.is_active and u.role == 'Superadmin')
def delete_syndic(request, syndic_id):
    syndic = get_object_or_404(CustomUser, id=syndic_id, role='Syndic')
    syndic.delete()
    messages.success(request, f'Syndic {syndic.nom} has been deleted.')
    return redirect('dashboard-superadmin')

# Delete Coproprietaire View
@user_passes_test(lambda u: u.is_active and u.role == 'Superadmin')
def delete_coproprietaire(request, coproprietaire_id):
    coproprietaire = get_object_or_404(Coproprietaire, user__id=coproprietaire_id)
    user = coproprietaire.user  # Access the linked CustomUser
    user.delete()  # Delete the CustomUser, which cascades the deletion to Coproprietaire
    messages.success(request, f'Coproprietaire {user.nom} has been deleted.')
    return redirect('dashboard-superadmin')

# Delete Prestataire View
@user_passes_test(lambda u: u.is_active and u.role == 'Superadmin')
def delete_prestataire(request, prestataire_id):
    prestataire = get_object_or_404(Prestataire, user__id=prestataire_id)
    user = prestataire.user  # Access the linked CustomUser
    user.delete()  # Delete the CustomUser, which cascades the deletion to Prestataire
    messages.success(request, f'Prestataire {user.nom} has been deleted.')
    return redirect('dashboard-superadmin')
