# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse

from apps.authentication.models import Syndic
from django.utils import timezone


@login_required(login_url="/login/")
def index(request):
    context = {
        'segment': 'index',
        'date': timezone.now().strftime("%a %d %B %Y")
        
        }
    try:
        syndic = Syndic.objects.get(user=request.user)
        context['syndic'] = syndic
    except Syndic.DoesNotExist:
        context['syndic'] = None

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def pages(request):
    context = {'date': timezone.now().strftime("%a %d %B %Y")}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    load_template = request.path.split('/')[-1]

    if load_template == 'admin':
        return HttpResponseRedirect(reverse('admin:index'))

    context['segment'] = load_template
    
    try:
        syndic = Syndic.objects.get(user=request.user)
        context['syndic'] = syndic
    except Syndic.DoesNotExist:
        context['syndic'] = None

    try:
        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))
    except template.TemplateDoesNotExist:
        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))
    except Exception as e:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))
