from __future__ import unicode_literals
import logging

from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.response import Response

from waves.models import Job, Service
from waves.api.serializers import JobSerializer, ServiceJobSerializer
from waves.utils import log_func_details
from . import WavesBaseView

logger = logging.getLogger(__name__)


class JobViewSet(viewsets.ModelViewSet, WavesBaseView):
    """
    API entry point for ServiceJobs
    """
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    parser_classes = (MultiPartParser, JSONParser)
    lookup_field = 'slug'

    def get_queryset(self):
        return Job.objects.all()

    @log_func_details
    def list(self, request, *args, **kwargs):
        queryset = Job.objects.get_user_job(user=request.user)
        serializer = JobSerializer(queryset,
                                   many=True,
                                   context={'request': request},
                                   fields=('url', 'created', 'status', 'service'))
        return Response(serializer.data)

    @log_func_details
    def retrieve(self, request, slug=None, *args, **kwargs):
        queryset = Job.objects.get_user_job(user=request.user)
        service_job = get_object_or_404(queryset,
                                        slug=slug)
        serializer = JobSerializer(service_job,
                                   context={'request': request})
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ServiceJobSerializer
        return super(JobViewSet, self).get_serializer_class()

    @log_func_details
    def get_serializer(self, *args, **kwargs):
        return super(JobViewSet, self).get_serializer(*args, **kwargs)

    @log_func_details
    def create(self, request, *args, **kwargs):
        if logger.isEnabledFor(logging.DEBUG):
            for param in request.data:
                logger.debug('param key ' + param)
                logger.debug(request.data[param])
            logger.debug('Request Data %s', request.data)
        request.data['client'] = request.user.pk
        return super(JobViewSet, self).create(request, *args, **kwargs)

    @log_func_details
    def perform_create(self, serializer):
        logger.debug('Request data %s', self.request.data)
        return super(JobViewSet, self).perform_create(serializer)
