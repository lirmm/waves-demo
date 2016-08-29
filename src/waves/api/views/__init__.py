from __future__ import unicode_literals

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication

from ..authentication.auth import WavesAPI_KeyAuthBackend


class WavesBaseView(APIView):
    authentication_classes = (WavesAPI_KeyAuthBackend, SessionAuthentication)
    permission_classes = (IsAuthenticated, )
