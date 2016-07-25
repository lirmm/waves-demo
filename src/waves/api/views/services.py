from __future__ import unicode_literals
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route

from waves.models import Service, ServiceInput, Job
from waves.exceptions import JobException
from waves.api.serializers import InputSerializer, ServiceSerializer, ServiceJobSerializer, JobSerializer
from . import WavesBaseView

import logging

logger = logging.getLogger(__name__)


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
                                       fields=('url', 'name', 'short_description', 'version', 'created', 'updated',
                                               'category')
                                       )
        return Response(serializer.data)

    def retrieve(self, request, api_name=None):
        queryset = Service.objects.get_public_services()
        service_tool = get_object_or_404(queryset, api_name=api_name)
        serializer = ServiceSerializer(service_tool, context={'request': request})
        return Response(serializer.data)

    @detail_route(methods=['post', 'get'], url_path='jobs')
    def submit_job(self, request, api_name=None):
        if request.POST:
            if logger.isEnabledFor(logging.DEBUG):
                for param in request.data:
                    logger.debug('param key ' + param)
                    logger.debug(request.data[param])
                logger.debug('Request Data %s', request.data)
            queryset = Service.objects.get_public_services()
            service = get_object_or_404(queryset, api_name=api_name)
            try:
                ass_email = request.data.pop('email')
            except KeyError:
                ass_email = None
            try:
                job = Service.objects.create_new_job(service=service,
                                                     email_to=ass_email,
                                                     submitted_inputs=request.data,
                                                     user=request.user)
                serializer = JobSerializer(job,
                                           many=False,
                                           context={'request': request},
                                           fields=('slug', 'url', 'created', 'status', ))
                return Response(serializer.data, status=201)
            except JobException as e:
                logger.fatal("Create Error %s", e.message)
                return Response({'error': 'An error occured'}, status=500)
        else:
            queryset = Service.objects.get_public_services()
            service_tool = get_object_or_404(queryset, api_name=api_name)
            queryset_jobs = Job.objects.get_service_job(user=request.user, service=service_tool)
            serializer = JobSerializer(queryset_jobs,
                                       many=True,
                                       context={'request': request},
                                       fields=('url', 'created', 'status', 'service'))
            return Response(serializer.data)


class ServiceJobViewSet(WavesBaseView):
    serializer_class = ServiceJobSerializer
    pass
