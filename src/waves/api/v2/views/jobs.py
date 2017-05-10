""" WAVES API jobs endpoints """
from __future__ import unicode_literals

from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import detail_route
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.response import Response

from ..serializers.jobs import JobSerializer, JobHistoryDetailSerializer, JobInputDetailSerializer, \
    JobOutputDetailSerializer
from waves.exceptions import WavesException
from waves.models import Job
from .base import WavesBaseView


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
        """ Basic job queryset """
        return Job.objects.get_user_job(self.request.user)

    def list(self, request, *args, **kwargs):
        """ List User's jobs (if any) from ListModelMixin """
        serializer = JobSerializer(self.get_queryset(), many=True, context={'request': request},
                                   fields=('url', 'slug', 'title', 'created', 'status_code', 'status_txt', 'service',
                                           'client'))
        return Response(serializer.data)

    def retrieve(self, request, slug=None, *args, **kwargs):
        """ Detailed job info """
        service_job = get_object_or_404(self.get_queryset(), slug=slug)
        serializer = JobSerializer(service_job, context={'request': request})
        return Response(serializer.data)

    def destroy(self, request, slug=None, *args, **kwargs):
        """ Try to remotely cancel job, then delete it from WAVES DB """
        service_job = get_object_or_404(self.get_queryset(), slug=slug)
        try:
            service_job.run_cancel()
        except WavesException as e:
            pass
        self.perform_destroy(service_job)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @detail_route(methods=['get'], url_path='history')
    def list_history(self, request, slug=None):
        """ List job history elements """
        queryset = Job.objects.get_user_job(user=request.user)
        job = get_object_or_404(queryset, slug=slug)
        serializer = JobHistoryDetailSerializer(job, many=False, context={'request': request})
        return Response(serializer.data)

    @detail_route(methods=['get'], url_path='inputs')
    def list_inputs(self, request, slug=None):
        """ list job submitted inputs """
        queryset = Job.objects.get_user_job(user=request.user)
        job = get_object_or_404(queryset, slug=slug)
        serializer = JobInputDetailSerializer(job, many=False, context={'request': request})
        return Response(serializer.data)

    @detail_route(methods=['get'], url_path='outputs')
    def list_outputs(self, request, slug=None):
        """ list job expected outputs """
        queryset = Job.objects.get_user_job(user=request.user)
        job = get_object_or_404(queryset, slug=slug)
        serializer = JobOutputDetailSerializer(job, many=False, context={'request': request})
        return Response(serializer.data)
