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
    lookup_field = 'api_name'

    def list(self, request, *args, **kwargs):
        return super(CategoryViewSet, self).list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return super(CategoryViewSet, self).retrieve(request, *args, **kwargs)
