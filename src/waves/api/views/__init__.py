""" WAVES API views """
from __future__ import unicode_literals

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication

from ..authentication.auth import WavesAPIKeyAuthBackend


class WavesBaseView(APIView):
    """ Base WAVES API view, set up for all subclasses permissions / authentication """
    authentication_classes = (WavesAPIKeyAuthBackend, SessionAuthentication)
    permission_classes = (IsAuthenticated, )
