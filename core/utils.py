# core.utils.py

from django.contrib import messages
from django_otp.decorators import otp_required
from django_otp import user_has_device
from functools import wraps

from django.utils import timezone
from django.utils.translation import activate, gettext as _, get_language, get_language_from_request

from core.middleware import get_current_request

from apps.dashboard.models import Superadmin, SuperSyndic, Syndic, Coproprietaire, Prestataire


def debug_language_cookie(request):
    current_language = get_language_from_request(request)
    print(f"Detected language from request: {current_language}")

def activate_current_language():
    """
    Activates the current language based on the LANGUAGE_CODE in the request.
    """
    current_request = get_current_request()
    if not current_request:
        print("No current request found.")
        return

    lang = current_request.POST.get('language') or getattr(current_request, 'LANGUAGE_CODE', None)
    if lang:
        print(f"Activating language: {lang}")
        activate(lang)
    else:
        print("LANGUAGE_CODE not found in the request.")

    print(f"Current language after activation: {get_language()}")


def get_user_context(user):
    context = {
        'date': timezone.now().strftime(_("%a %d %B %Y")),
        'superadmin': None,
        'supersyndic': None,
        'supersyndic_id': None,
        'syndic': None,
        'syndic_id': None,
        'coproprietaire': None,
        'coproprietaire_id': None,
        'prestataire': None,
        'prestataire_id': None,
    }

    # Check for each role and populate context
    try:
        superadmin = Superadmin.objects.get(user=user)
        context['superadmin'] = superadmin
    except Superadmin.DoesNotExist:
        pass

    try:
        supersyndic = SuperSyndic.objects.get(user=user)
        context['supersyndic'] = supersyndic
        context['supersyndic_id'] = supersyndic.id
    except SuperSyndic.DoesNotExist:
        pass

    try:
        syndic = Syndic.objects.get(user=user)
        context['syndic'] = syndic
        context['syndic_id'] = syndic.id
    except Syndic.DoesNotExist:
        pass

    try:
        coproprietaire = Coproprietaire.objects.get(user=user)
        context['coproprietaire'] = coproprietaire
        context['coproprietaire_id'] = coproprietaire.id
    except Coproprietaire.DoesNotExist:
        pass

    try:
        prestataire = Prestataire.objects.get(user=user)
        context['prestataire'] = prestataire
        context['prestataire_id'] = prestataire.id
    except Prestataire.DoesNotExist:
        pass

    return context


def otp_required_for_supersyndic(view_func):
    """
    Custom decorator to apply @otp_required only for users with the 'SuperSyndic' role.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.role == 'SuperSyndic':
            if not user_has_device(request.user):
                return messages.warning(request,_("OTP device not found for this user."), status=403)
            return otp_required(view_func)(request, *args, **kwargs)
        return view_func(request, *args, **kwargs)
    return _wrapped_view
