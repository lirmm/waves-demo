from __future__ import unicode_literals
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions
from rest_framework.response import Response

from waves.models import Service, ServiceInput
from waves.api.serializers import InputSerializer, ServiceSerializer
from . import WavesBaseView


class ServiceInputViewSet(viewsets.ReadOnlyModelViewSet, WavesBaseView):
    """
    Api entry point to ServiceInputs
    """
    serializer_class = InputSerializer

    def get_queryset(self):
        return ServiceInput.objects.filter(tool__pk=self.kwargs['service'],
                                           conditionalqsdqsdinput=None,
                                           conditionalwhen=None)


class ServiceViewSet(viewsets.ModelViewSet, WavesBaseView):
    """
    API entry point to Services
    """
    # TODO filter by client / services associations
    serializer_class = ServiceSerializer
    lookup_field = 'api_name'

    def get_queryset(self):
        return Service.objects.get_public_services()

    def list(self, request):
        queryset = Service.objects.get_public_services()
        serializer = ServiceSerializer(queryset, many=True, context={'request': request},
                                       fields=('url', 'name', 'description', 'version', 'created', 'updated',
                                               'category', 'id')
                                       )
        return Response(serializer.data)

    def retrieve(self, request, api_name=None):
        queryset = Service.objects.get_public_services()
        service_tool = get_object_or_404(queryset, api_name=api_name)
        serializer = ServiceSerializer(service_tool, context={'request': request})
        return Response(serializer.data)
