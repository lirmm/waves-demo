from __future__ import unicode_literals
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework import status
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


class ServiceViewSet(viewsets.ReadOnlyModelViewSet, WavesBaseView):
    """
    API entry point to Services
    """
    serializer_class = ServiceSerializer
    lookup_field = 'api_name'

    def get_queryset(self):
        return Service.objects.get_public_services()

    def list(self, request):
        queryset = Service.objects.get_public_services()
        serializer = ServiceSerializer(queryset, many=True, context={'request': request},
                                       fields=('url', 'name', 'short_description', 'version', 'created', 'updated',
                                               'category', 'jobs')
                                       )
        return Response(serializer.data)

    def retrieve(self, request, api_name=None):
        queryset = Service.objects.get_public_services()
        service_tool = get_object_or_404(queryset, api_name=api_name)
        serializer = ServiceSerializer(service_tool, context={'request': request})
        return Response(serializer.data)

    @detail_route(methods=['post', 'get'], url_path='jobs')
    def service_job(self, request, api_name=None):
        if request.POST:
            # CREATE A NEW JOB
            if logger.isEnabledFor(logging.DEBUG):
                for param in request.data:
                    logger.debug('param key ' + param)
                    logger.debug(request.data[param])
                logger.debug('Request Data %s', request.data)
            queryset = Service.objects.get_public_services()
            service = get_object_or_404(queryset, api_name=api_name)
            ass_email = request.data.pop('email', None)
            try:
                request.data.pop('api_key')
                submitted_data = {
                    'service': service.pk,
                    'client': request.user.pk,
                    'inputs': request.data
                }
                # serializer = ServiceJobSerializer(many=False, context={'request': request},data=request.data)
                serializer = self.get_serializer(context={'request': request},
                                                 fields=('inputs',))
                serializer.run_validation(data=submitted_data,)
                job = Service.objects.create_new_job(service=service,
                                                     email_to=ass_email,
                                                     submitted_inputs=request.data,
                                                     user=request.user)
                serializer = JobSerializer(job,
                                           many=False,
                                           context={'request': request},
                                           fields=('slug', 'url', 'created', 'status',))
                return Response(serializer.data, status=201)
            except JobException as e:
                logger.fatal("Create Error %s", e.message)
                return Response({'error': e.message}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # RETRIEVE A SERVICE JOB
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