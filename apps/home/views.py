# -*- encoding: utf-8 -*- apps/home/views.py

"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.utils.translation import gettext as _
from django.utils import timezone
#
from core.utils import get_user_context


@login_required(login_url="/login/")
def pages(request):
    context = get_user_context(request.user)
    context.update({
        'titlePage': _('Dashboard') + f" {request.user.nom}",
        'nom': request.user.nom,
        'date': timezone.now().strftime(_("%a %d %B %Y"))
        })
    
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    # Determine which template to load
    load_template = request.path.split('/')[-1]

    if load_template == 'admin':
        return HttpResponseRedirect(reverse('admin:index'))

    context['segment'] = load_template

    try:
        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))
    except template.TemplateDoesNotExist:
        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))
    except Exception as e:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def index(request):
    context = get_user_context(request.user)
    context.update({
        'segment': 'index',
        'titlePage': _('Dashboard') + f" {request.user.nom}",
        'nom': request.user.nom,
        'date': timezone.now().strftime(_("%a %d %B %Y")),
        })

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))
