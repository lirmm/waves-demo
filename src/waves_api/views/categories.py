""" WAVES API categories endpoints """
from __future__ import unicode_literals

from rest_framework import viewsets

from waves_api.serializers import CategorySerializer
from waves.models import ServiceCategory
from waves_api.views.base import WavesBaseView


class CategoryViewSet(viewsets.ReadOnlyModelViewSet, WavesBaseView):
    """
    API entry point to list services categories
    """
    queryset = ServiceCategory.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'api_name'
