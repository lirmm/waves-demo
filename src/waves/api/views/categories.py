from __future__ import unicode_literals

from rest_framework import viewsets

from waves.models import ServiceCategory
from waves.api.serializers import CategorySerializer
from . import WavesBaseView


class CategoryViewSet(viewsets.ReadOnlyModelViewSet, WavesBaseView):
    """
    API entry point to list services categories
    """
    queryset = ServiceCategory.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'name'
