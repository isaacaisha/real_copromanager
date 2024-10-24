# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .forms import LoginForm, SignUpForm, LicenseForm
from .models import CustomUser, License, Superadmin, Syndic, Coproprietaire, Prestataire, Immeuble
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
        try:
            syndic = Syndic.objects.get(user=user)  # Fetch the syndic instance
            return redirect('dashboard-syndic', syndic_id=syndic.id)  # Redirect with syndic_id
        except Syndic.DoesNotExist:
            messages.error(request, 'Syndic profile not found.')
            return redirect('home')  # Redirect to home if no syndic is found

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


#@user_passes_test(lambda user: user.role == 'Superadmin')
def register_user(request):
    msg = None
    success = False

    if request.method == "POST":
        form = SignUpForm(request.POST)
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
                print(f"Syndic created: {syndic}")
                # Create a License instance linked to the newly created Syndic
                license_form = LicenseForm(request.POST)
                if license_form.is_valid():
                    license = license_form.save(commit=False)
                    license.syndic = syndic  # Link license to the Syndic
                    license.save()

                    ## Assign the license to the syndic and save
                    #syndic.license = license
                    #syndic.save()
                    
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

    context = {
        'form': form,
        'msg': msg,
        'success': success,
        'date': timezone.now().strftime("%a %d %B %Y")
    }

    return render(request, "accounts/register.html", context)


# Delete Syndic View
@user_passes_test(lambda user: user.role == 'Superadmin')
@user_passes_test(lambda u: u.is_active and u.role == 'Superadmin')
def delete_syndic(request, syndic_id):
    syndic = get_object_or_404(CustomUser, id=syndic_id, role='Syndic')
    syndic.delete()
    messages.success(request, f'Syndic {syndic.nom} has been deleted.')
    return redirect('dashboard-superadmin')

# Delete Coproprietaire View
@user_passes_test(lambda user: user.role == 'Superadmin')
@user_passes_test(lambda u: u.is_active and u.role == 'Superadmin')
def delete_coproprietaire(request, coproprietaire_id):
    coproprietaire = get_object_or_404(Coproprietaire, user__id=coproprietaire_id)
    user = coproprietaire.user  # Access the linked CustomUser
    user.delete()  # Delete the CustomUser, which cascades the deletion to Coproprietaire
    messages.success(request, f'Coproprietaire {user.nom} has been deleted.')
    return redirect('dashboard-superadmin')

# Delete Prestataire View
@user_passes_test(lambda user: user.role == 'Superadmin')
@user_passes_test(lambda u: u.is_active and u.role == 'Superadmin')
def delete_prestataire(request, prestataire_id):
    prestataire = get_object_or_404(Prestataire, user__id=prestataire_id)
    user = prestataire.user  # Access the linked CustomUser
    user.delete()  # Delete the CustomUser, which cascades the deletion to Prestataire
    messages.success(request, f'Prestataire {user.nom} has been deleted.')
    return redirect('dashboard-superadmin')


# Superadmin dashboard
@login_required
@user_passes_test(lambda user: user.role == 'Superadmin')
def dashboard_superadmin(request):
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

    coproprietaires = CustomUser.objects.filter(role='Coproprietaire')
    prestataires = CustomUser.objects.filter(role='Prestataire')

    context = {
        'syndics': syndics,
        'coproprietaires': coproprietaires,
        'prestataires': prestataires,
        'username': request.user.username,
        'date': timezone.now().strftime("%a %d %B %Y")
    }

    return render(request, 'home/dashboard-superadmin.html', context)


# View for license customization
@login_required
@user_passes_test(lambda u: u.is_active and u.role == 'Superadmin')
def customize_license(request, license_id):
    license = get_object_or_404(License, id=license_id)
    if request.method == 'POST':
        license_form = LicenseForm(request.POST, instance=license)
        if license_form.is_valid():
            license.est_personnalise = license_form.cleaned_data.get('est_personnalise', True)
            license.save()
            return redirect('license-detail', license_id=license.id)
    else:
        license_form = LicenseForm(instance=license)

    context = {
        'license_form': license_form,
        'license': license,
        'date': timezone.now().strftime("%a %d %B %Y")
    }

    return render(request, 'home/customize-license.html', context)


# View to display license details
@login_required
def license_detail(request, license_id):
    license = get_object_or_404(License, id=license_id)
    syndic = license.syndic  # Access the syndic associated with this license
    coproprietaires = syndic.coproprietaire_set.all() if syndic else []
    prestataires = syndic.prestataire_set.all() if syndic else []
    immeubles = syndic.immeuble_set.all() if syndic else []
    
    context = {
        'license': license,
        'syndic': syndic,
        'coproprietaires': coproprietaires,
        'prestataires': prestataires,
        'immeubles': immeubles,
        #'syndic_id': syndic.id if syndic else None,
        'date': timezone.now().strftime("%a %d %B %Y")
    }
    return render(request, 'home/license-detail.html', context)


# Syndic dashboard
@login_required
def dashboard_syndic(request, syndic_id):
    try:
        # Fetch the current logged-in user's syndic profile
        syndic = Syndic.objects.get(id=syndic_id)
        
        # Retrieve relevant syndic information, such as buildings and co-owners
        immeubles = Immeuble.objects.filter(syndic=syndic)
        coproprietaires = Coproprietaire.objects.filter(syndic=syndic)
        # Retrieve the license for the logged-in syndic, handle multiple licenses if necessary
        license = License.objects.filter(syndic__user=request.user).order_by('-date_debut').first()
        #if not license:
        #    messages.warning(request, 'No license found for this syndic.')
        
        context = {
            'syndic': syndic,
            'license': license,
            'immeubles': immeubles,
            'coproprietaires': coproprietaires,
            'date': timezone.now().strftime("%a %d %B %Y")
        }

        return render(request, 'home/dashboard-syndic.html', context)

    except Syndic.DoesNotExist:
        # Handle the case where the syndic doesn't exist (e.g., if a user tries to access this page without being a syndic)
        context = {
            'message': 'Syndic profile not found.',
            'date': timezone.now().strftime("%a %d %B %Y"),
        }
        return render(request, 'home/dashboard-syndic.html', context)


@login_required
def dashboard_coproprietaire(request):
    """
    View for the coproprietaire dashboard.
    This view should display information relevant to coproprietaires, 
    such as co-owner documents, charges, and announcements.
    """
    coproprietaires = Coproprietaire.objects.all()
    context = {
        'coproprietaires': coproprietaires,
        'date': timezone.now().strftime("%a %d %B %Y")
    }

    return render(request, 'home/dashboard-coproprietaire.html', context)


@login_required
def dashboard_prestataire(request):
    """
    View for the prestataire dashboard.
    This view should display information relevant to prestataires,
    such as assigned tasks, projects, or service requests.
    """
    prestataires = Prestataire.objects.all()

    context = {
        'prestataires': prestataires,
        'date': timezone.now().strftime("%a %d %B %Y")
    }

    return render(request, 'home/dashboard-prestataire.html', context)
