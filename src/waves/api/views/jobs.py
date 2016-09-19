from __future__ import unicode_literals
import logging

from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route

from waves.models import Job
from waves.api.serializers.jobs import JobSerializer, JobHistoryDetailSerializer, \
    JobInputDetailSerializer, JobOutputDetailSerializer
from . import WavesBaseView

logger = logging.getLogger(__name__)


class JobViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin,
                 viewsets.GenericViewSet, WavesBaseView):
    """
    API entry point for ServiceJobs
    """
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    parser_classes = (MultiPartParser, JSONParser)
    lookup_field = 'slug'

    def get_queryset(self):
        return Job.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = Job.objects.get_user_job(user=request.user)
        serializer = JobSerializer(queryset,
                                   many=True,
                                   context={'request': request},
                                   fields=('url', 'slug', 'title', 'created', 'status_code', 'status_txt', 'service',
                                           'client'))
        return Response(serializer.data)

    def retrieve(self, request, slug=None, *args, **kwargs):
        queryset = Job.objects.get_user_job(user=request.user)
        service_job = get_object_or_404(queryset,
                                        slug=slug)
        serializer = JobSerializer(service_job,
                                   context={'request': request})
        return Response(serializer.data)

    def destroy(self, request, slug=None, *args, **kwargs):
        queryset = Job.objects.get_user_job(user=request.user)
        service_job = get_object_or_404(queryset, slug=slug)
        return Response(self.get_serializer(request=request).data)

    def update(self, request, slug=None):
        return Response(self.get_serializer(request=request).data)

    def partial_update(self, request, slug=None):
        return Response(self.get_serializer(request=request).data)

    @detail_route(methods=['get'], url_path='history')
    def list_history(self, request, slug=None):
        queryset = Job.objects.get_user_job(user=request.user)
        job = get_object_or_404(queryset, slug=slug)
        serializer = JobHistoryDetailSerializer(job,
                                                many=False,
                                                context={'request': request})
        return Response(serializer.data)

    @detail_route(methods=['get'], url_path='inputs')
    def list_inputs(self, request, slug=None):
        queryset = Job.objects.get_user_job(user=request.user)
        job = get_object_or_404(queryset, slug=slug)
        serializer = JobInputDetailSerializer(job,
                                              many=False,
                                              context={'request': request})
        return Response(serializer.data)

    @detail_route(methods=['get'], url_path='outputs')
    def list_outputs(self, request, slug=None):
        queryset = Job.objects.get_user_job(user=request.user)
        job = get_object_or_404(queryset, slug=slug)
        serializer = JobOutputDetailSerializer(job,
                                               many=False,
                                               context={'request': request})
        return Response(serializer.data)
