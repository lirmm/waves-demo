from django.contrib.auth import user_logged_in
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.authentication import BaseAuthentication

from profiles.models import UserProfile


class APIKeyAuthBackend(BaseAuthentication):
    """ API (public key) authentication backend """
    def authenticate(self, request):
        """ Authenticate from waves_api GET or POST 'api_key' param"""
        api_key = request.POST.get('api_key', request.GET.get('api_key', None))
        if not api_key:
            return None
        try:
            api_prof = UserProfile.objects.get(api_key=api_key)
            if not api_prof.banned:
                # Authorized all 'api_key' except when user is banned
                user_logged_in.send(sender=api_prof.__class__, request=request, user=api_prof.user)
                return api_prof.user, None
        except ObjectDoesNotExist:
            return None, None
        return None, None
