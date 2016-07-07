from __future__ import unicode_literals

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.authentication import BaseAuthentication

from waves.models import APIProfile


class WavesAPI_KeyAuthBackend(BaseAuthentication):
    def authenticate(self, request):
        api_key = request.POST.get('api_key', request.GET.get('api_key', None))
        if not api_key:
            return None
        try:
            # Validate API KEY
            api_prof = APIProfile.objects.get(api_key=api_key)
            if settings.WAVES_GROUP_API in api_prof.user.groups.values_list(
                    'name', flat=True) or api_prof.user.is_superuser or api_prof.user.is_staff:
                return api_prof.user, None
        except ObjectDoesNotExist:
            return None, None
        return None, None
