from django.utils import timezone
from .models import Superadmin, SuperSyndic, Syndic, Coproprietaire, Prestataire

from django.http import HttpResponse
from django_otp.decorators import otp_required
from django_otp import user_has_device
from functools import wraps


def get_user_context(user):
    context = {
        'date': timezone.now().strftime("%a %d %B %Y"),
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
                return HttpResponse("OTP device not found for this user.", status=403)
            return otp_required(view_func)(request, *args, **kwargs)
        return view_func(request, *args, **kwargs)
    return _wrapped_view
