## -*- encoding: utf-8 -*-
#"""
#Copyright (c) 2019 - present AppSeed.us
#"""
#
#from django import template
#from django.contrib.auth.decorators import login_required, user_passes_test
#from django.http import HttpResponse, HttpResponseRedirect
#from django.shortcuts import get_object_or_404, redirect
#from django.contrib import messages
#from django.template import loader
#from django.urls import reverse
#
#from django_otp.decorators import otp_required
#
#from apps.authentication.forms import SuperSyndicForm
#from apps.dashboard.forms import LicenseForm
#from apps.authentication.models import CustomUser
#from apps.dashboard.models import (
#    License, Superadmin, SuperSyndic,
#    Syndic, Coproprietaire, Prestataire, Immeuble
#    )
#
#from django.db.models import Q  # Import Q for complex queries
#
#from django.utils import timezone
#
#
#@login_required
#@user_passes_test(lambda u: u.is_active and 
#                  (u.role == 'Superadmin' 
#                   or u.role == 'Syndic' 
#                   or u.role == 'SuperSyndic'))
#def user_search(request):
#    query = request.GET.get('q', '').strip()  # Get the search query from the GET request
#    print(f"Search Query: {query}")  # Debug statement
#    
#    # Filter by 'nom' or 'email', case-insensitive
#    users = CustomUser.objects.filter(
#        Q(nom__icontains=query) | Q(email__icontains=query)
#    )
#
#    context = {
#        'dont_show_syndic_btn': True,
#        'users': users,
#        'query': query,
#        'titlePage': f'Résultat pour: "{query}"',
#        'date': timezone.now().strftime("%a %d %B %Y")
#    }
#    
#    html_template = loader.get_template('dashboard/search-results.html')
#    return HttpResponse(html_template.render(context, request))
#
#
#@login_required
#def user_profile(request, user_id):
#    user = get_object_or_404(CustomUser, id=user_id)
#    
#    # Get related data based on user role
#    related_data = {}
#    if user.role == 'SuperSyndic':
#        related_data['super_syndic'] = get_object_or_404(Syndic, user=user)
#        related_data['super_syndic_licenses'] = License.objects.filter(super_syndic=related_data['super_syndic'])
#    elif user.role == 'Syndic':
#        related_data['syndic'] = get_object_or_404(Syndic, user=user)
#        related_data['syndic_licenses'] = License.objects.filter(syndic=related_data['syndic'])
#    elif user.role == 'Coproprietaire':
#        related_data['coproprietaire'] = get_object_or_404(Coproprietaire, user=user)
#    elif user.role == 'Prestataire':
#        related_data['prestataire'] = get_object_or_404(Prestataire, user=user)
#
#    context = {
#        'user': user,
#        'related_data': related_data,
#        'titlePage': f'Profile of {user.nom}',
#        'date': timezone.now().strftime("%a %d %B %Y"),
#    }
#
#    html_template = loader.get_template('dashboard/user-profile.html')
#    return HttpResponse(html_template.render(context, request))
#
#
## Superadmin dashboard
#@login_required
#@user_passes_test(lambda u: u.is_active and u.role == 'Superadmin')
#def dashboard_superadmin(request):
#    # Retrieve all Super Syndics, Syndics, and other roles
#    super_syndics = CustomUser.objects.filter(role='SuperSyndic')
#    syndics = CustomUser.objects.filter(role='Syndic')
#    coproprietaires = CustomUser.objects.filter(role='Coproprietaire')
#    prestataires = CustomUser.objects.filter(role='Prestataire')
#
#    # Add a license field to each Super Syndic
#    for super_syndic in super_syndics:
#        try:
#            super_syndic_instance = SuperSyndic.objects.get(user=super_syndic)
#            # Retrieve the most recent license for the Super Syndic
#            super_syndic.license = (
#                License.objects.filter(super_syndic=super_syndic_instance)
#                .order_by('-date_debut')
#                .first()
#            )
#        except SuperSyndic.DoesNotExist:
#            # Handle the case where the CustomUser is not associated with a SuperSyndic
#            super_syndic.license = None
#
#    # Add a license field to each syndic
#    for syndic in syndics:
#        try:
#            # Retrieve the Syndic instance
#            syndic_instance = Syndic.objects.get(user=syndic)
#            # Retrieve the most recent license for the Syndic
#            syndic.license = (
#                License.objects.filter(syndic=syndic_instance)
#                .order_by('-date_debut')
#                .first()
#            )
#        except Syndic.DoesNotExist:
#            # Handle the case where the CustomUser is not associated with a Syndic
#            syndic.license = None
#
#    # Prepare context
#    context = {
#        'segment': 'dashboard-superadmin',
#        'super_syndics': super_syndics,
#        'syndics': syndics,
#        'coproprietaires': coproprietaires,
#        'prestataires': prestataires,
#        'titlePage': 'Dashboard Super Admin',
#        'date': timezone.now().strftime("%a %d %B %Y")
#    }
#
#    # Render template
#    html_template = loader.get_template('home/dashboard-superadmin.html')
#    return HttpResponse(html_template.render(context, request))
#
#
#@login_required
#@user_passes_test(lambda u: u.is_active and u.role == 'Superadmin')
#def gestion_super_syndic(request):
#    """
#    View for managing SuperSyndic users.
#    Only accessible to users with the role of 'Superadmin'.
#    """
#    # Get all SuperSyndic users
#    super_syndics = CustomUser.objects.filter(role='SuperSyndic')
#
#    # Attach related license data to each super_syndic
#    for super_syndic in super_syndics:
#        try:
#            super_syndic_instance = SuperSyndic.objects.get(user=super_syndic)
#            # Retrieve the most recent license for the super_syndic
#            super_syndic.license = License.objects.filter(
#                super_syndic=super_syndic_instance
#            ).order_by('-date_debut').first()
#        except SuperSyndic.DoesNotExist:
#            # Handle the case where the CustomUser is not associated with a SuperSyndic
#            super_syndic.license = None
#
#    context = {
#        'segment': 'gestion-super-syndic',
#        'super_syndics': super_syndics,
#        'titlePage': 'Gestion Super Syndic',
#        'date': timezone.now().strftime("%a %d %B %Y"),
#    }
#
#    html_template = loader.get_template('home/gestion-super-syndic.html')
#    return HttpResponse(html_template.render(context, request))
#
#
#@user_passes_test(lambda u: u.is_active and u.role == 'Superadmin')
#def gestion_syndic(request):
#    form = SuperSyndicForm()
#    syndics = CustomUser.objects.filter(role='Syndic')
#
#    # Add a license field to each syndic
#    for syndic in syndics:
#        # Get the Syndic instance associated with the CustomUser (if exists)
#        try:
#            syndic_instance = Syndic.objects.get(user=syndic)
#            # Retrieve the most recent license for the syndic
#            syndic.license = License.objects.filter(syndic=syndic_instance).order_by('-date_debut').first()
#        except Syndic.DoesNotExist:
#            # Handle the case where the CustomUser is not associated with a Syndic
#            syndic.license = None
#
#    context = {
#        'segment': 'gestion-syndic',
#        'form': form,
#        'syndics': syndics,
#        'titlePage': 'Gestion Syndic',
#        'date': timezone.now().strftime("%a %d %B %Y")
#    }
#
#    html_template = loader.get_template('home/gestion-syndic.html')
#    return HttpResponse(html_template.render(context, request))
#
#
#@user_passes_test(lambda u: u.is_active and u.role == 'Superadmin')
#def gestion_coproprietaire(request):
#    coproprietaires = CustomUser.objects.filter(role='Coproprietaire')
#
#    context = {
#        'segment': 'gestion-coproprietaire',
#        'coproprietaires': coproprietaires,
#        'titlePage': 'Gestion Coproprietaire',
#        'date': timezone.now().strftime("%a %d %B %Y")
#    }
#
#    html_template = loader.get_template('home/gestion-coproprietaire.html')
#    return HttpResponse(html_template.render(context, request))
#
#
#@user_passes_test(lambda u: u.is_active and u.role == 'Superadmin')
#def gestion_prestataire(request):
#    prestataires = CustomUser.objects.filter(role='Prestataire')
#
#    context = {
#        'segment': 'gestion-prestataire',
#        'prestataires': prestataires,
#        'titlePage': 'Gestion prestataire',
#        'date': timezone.now().strftime("%a %d %B %Y")
#    }
#
#    html_template = loader.get_template('home/gestion-prestataire.html')
#    return HttpResponse(html_template.render(context, request))
#
#
## View for license customization
#@login_required
#@user_passes_test(lambda u: u.is_active and u.role == 'Superadmin')
#def customize_license(request, license_id):
#    license = get_object_or_404(License, id=license_id)
#    if request.method == 'POST':
#        license_form = LicenseForm(request.POST, instance=license)
#        if license_form.is_valid():
#            license.est_personnalise = license_form.cleaned_data.get('est_personnalise', True)
#            license.save()
#            return redirect('license-detail', license_id=license.id)
#    else:
#        license_form = LicenseForm(instance=license)
#
#    context = {
#        'segment': 'customize-license',
#        'license_form': license_form,
#        'license': license,
#        'id': license.id if license else None,
#        'titlePage': 'Configuration License',
#        'date': timezone.now().strftime("%a %d %B %Y")
#    }
#
#    html_template = loader.get_template('home/customize-license.html')
#    return HttpResponse(html_template.render(context, request))
#
#
## View to display license details
#@login_required
#@user_passes_test(lambda u: u.is_active and u.role == 'Superadmin')
#def license_detail(request, license_id):
#    license = get_object_or_404(License, id=license_id)
#    syndic = license.syndic  # Access the syndic associated with this license
#    coproprietaires = syndic.coproprietaire_set.all() if syndic else []
#    prestataires = syndic.prestataire_set.all() if syndic else []
#    immeubles = syndic.immeuble_set.all() if syndic else []
#    
#    context = {
#        'segment': 'license-detail',
#        'license': license,
#        'syndic': syndic,
#        'coproprietaires': coproprietaires,
#        'prestataires': prestataires,
#        'immeubles': immeubles,
#        'titlePage': 'License Détail',
#        'date': timezone.now().strftime("%a %d %B %Y")
#    }
#    
#    html_template = loader.get_template('home/license-detail.html')
#    return HttpResponse(html_template.render(context, request))
#
#
## View for the Super Syndic page, requiring 2FA status
#@login_required
#@otp_required
#@user_passes_test(lambda u: u.is_active and (u.role == 'Superadmin' or u.role == 'SuperSyndic'))
#def dashboard_super_syndic(request, super_syndic_id):
#    titlePage = 'Super Syndic Dashboard'
#
#    # Fetch the current logged-in user's syndic profile
#    try:
#        # Fetch the current syndic profile
#        if request.user.role == 'Superadmin':
#            # Query by user__id when accessed by Superadmin
#            super_syndic = get_object_or_404(SuperSyndic, user__id=super_syndic_id)
#        else:
#            # Restrict to the currently logged-in syndic
#            super_syndic = get_object_or_404(SuperSyndic, user=request.user)
#
#        ## Retrieve relevant syndic information, such as buildings and co-owners
#        #immeubles = Immeuble.objects.filter(super_syndic=super_syndic)
#        #coproprietaires = Coproprietaire.objects.filter(super_syndic=super_syndic)
#            
#        # Retrieve the license for the logged-in syndic, handle multiple licenses if necessary
#        license = License.objects.filter(super_syndic=super_syndic).order_by('-date_debut').first()
#        if not license:
#            messages.warning(request, 'No license found for this syndic.')
#        
#        context = {
#            'segment': 'dashboard-super-syndic',
#            'super_syndic': super_syndic,
#            #'super_syndic_id': super_syndic_id,
#            'license': license,
#            #'immeubles': immeubles,
#            #'coproprietaires': coproprietaires,
#            'titlePage': titlePage,
#            'date': timezone.now().strftime("%a %d %B %Y")
#        }
#
#        html_template = loader.get_template('home/dashboard-super-syndic.html')
#        return HttpResponse(html_template.render(context, request))
#
#    except SuperSyndic.DoesNotExist:
#        # Handle the case where the syndic doesn't exist (e.g., if a user tries to access this page without being a syndic)
#        context = {
#            'segment': 'dashboard-super-syndic',
#            'message': 'Super Syndic profile not found.',
#            'titlePage': 'Dashboard',
#            'date': timezone.now().strftime("%a %d %B %Y"),
#        }
#        
#        html_template = loader.get_template('home/dashboard-super-syndic.html')
#        return HttpResponse(html_template.render(context, request))
#
#
## Syndic dashboard
#@login_required
#@user_passes_test(lambda u: u.is_active and (u.role == 'Superadmin' or u.role == 'Syndic'))
#def dashboard_syndic(request, syndic_id):
#    try:
#        # Fetch the current syndic profile
#        if request.user.role == 'Superadmin':
#            # Query by user__id when accessed by Superadmin
#            syndic = get_object_or_404(Syndic, user__id=syndic_id)
#        else:
#            # Restrict to the currently logged-in syndic
#            syndic = get_object_or_404(Syndic, user=request.user)
#
#        ## Fetch the current logged-in user's syndic profile
#        ##syndic = Syndic.objects.get(id=syndic_id)
#        #syndic = get_object_or_404(Syndic, id=syndic_id)
#
#        # Retrieve relevant syndic information, such as buildings and co-owners
#        immeubles = Immeuble.objects.filter(syndic=syndic)
#        coproprietaires = Coproprietaire.objects.filter(syndic=syndic)
#        # Retrieve the license for the logged-in syndic, handle multiple licenses if necessary
#        license = License.objects.filter(syndic=syndic).order_by('-date_debut').first()
#        if not license:
#            messages.warning(request, 'No license found for this syndic.')
#        
#        context = {
#            'segment': 'dashboard-syndic',
#            'syndic': syndic,
#            'license': license,
#            'immeubles': immeubles,
#            'coproprietaires': coproprietaires,
#            'titlePage': 'Dashboard',
#            'date': timezone.now().strftime("%a %d %B %Y")
#        }
#
#        html_template = loader.get_template('home/dashboard-syndic.html')
#        return HttpResponse(html_template.render(context, request))
#
#    except Syndic.DoesNotExist:
#        # Handle the case where the syndic doesn't exist (e.g., if a user tries to access this page without being a syndic)
#        context = {
#            'segment': 'dashboard-syndic',
#            'message': 'Syndic profile not found.',
#            'titlePage': 'Dashboard',
#            'date': timezone.now().strftime("%a %d %B %Y"),
#        }
#        
#        html_template = loader.get_template('home/dashboard-syndic.html')
#        return HttpResponse(html_template.render(context, request))
#
#
#@login_required
#@user_passes_test(lambda u: u.is_active and (u.role == 'Superadmin' or u.role == 'Coproprietaire'))
#def dashboard_coproprietaire(request, coproprietaire_id):
#    """
#    View for the coproprietaire dashboard.
#    This view should display information relevant to coproprietaires, 
#    such as co-owner documents, charges, and announcements.
#    """
#
#    # Fetch the current coproprietaire profile
#    if request.user.role == 'Superadmin':
#        # Query by user__id when accessed by Superadmin
#        coproprietaire = get_object_or_404(Coproprietaire, user__id=coproprietaire_id)
#    else:
#        # Restrict to the currently logged-in coproprietaire
#        coproprietaire = get_object_or_404(Coproprietaire, user=request.user)
#
#    # Retrieve the syndic associated with this prestataire
#    syndic = coproprietaire.syndic if hasattr(coproprietaire, 'syndic') else None
#
#    # Retrieve the license associated with the syndic
#    license = syndic.licence if syndic and hasattr(syndic, 'licence') else None
#    
#     # Only fetch the coproprietaires associated with the current syndic
#    if request.user.role == 'Superadmin':
#        coproprietaires = Coproprietaire.objects.all()  # Superadmin can see all
#    else:
#        coproprietaires = Coproprietaire.objects.filter(syndic=syndic, user=request.user)  # Filter by syndic for others
#    
#    context = {
#        'segment': 'dashboard-coproprietaire',
#        'coproprietaire': coproprietaire,
#        'coproprietaires': coproprietaires,
#        'syndic': syndic,
#        'license': license,
#        'titlePage': 'Dashboard',
#        'date': timezone.now().strftime("%a %d %B %Y")
#    }
#
#    html_template = loader.get_template('home/dashboard-coproprietaire.html')
#    return HttpResponse(html_template.render(context, request))
#
#
#@login_required
#@user_passes_test(lambda u: u.is_active and( u.role == 'Superadmin' or u.role == 'Prestataire'))
#def dashboard_prestataire(request, prestataire_id):
#    """
#    View for the prestataire dashboard.
#    This view should display information relevant to prestataires,
#    such as assigned tasks, projects, or service requests.
#    """
#
#    # Fetch the current prestataire profile
#    if request.user.role == 'Superadmin':
#        # Query by user__id when accessed by Superadmin
#        prestataire = get_object_or_404(Prestataire, user__id=prestataire_id)
#    else:
#        # Restrict to the currently logged-in prestataire
#        prestataire = get_object_or_404(Prestataire, user=request.user)
#
#    # Retrieve the syndic associated with this prestataire
#    syndic = prestataire.syndic if hasattr(prestataire, 'syndic') else None
#
#    # Retrieve the license associated with the syndic
#    license = syndic.licence if syndic and hasattr(syndic, 'licence') else None
#
#    
#    # Only fetch the prestataires associated with the current syndic
#    if request.user.role == 'Superadmin':
#        prestataires = Prestataire.objects.all()  # Superadmin can see all
#    else:
#        prestataires = Prestataire.objects.filter(syndic=syndic, user=request.user)  # Filter by syndic for others
#
#    context = {
#        'segment': 'dashboard-prestataire',
#        'prestataire': prestataire,
#        'prestataires': prestataires,
#        'syndic': syndic,
#        'license': license,
#        'titlePage': 'Dashboard',
#        'date': timezone.now().strftime("%a %d %B %Y")
#    }
#
#    html_template = loader.get_template('home/dashboard-prestataire.html')
#    return HttpResponse(html_template.render(context, request))
#