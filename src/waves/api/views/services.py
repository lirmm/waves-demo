from __future__ import unicode_literals
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import detail_route, list_route
from waves.models import Service, ServiceInput, Job, ServiceSubmission
from waves.exceptions import JobException
from waves.api.serializers import InputSerializer, ServiceSerializer, MetaSerializer, \
    JobSerializer, ServiceFormSerializer, ServiceMetaSerializer, ServiceSubmissionSerializer
from waves.managers.servicejobs import ServiceJobManager
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
        return Service.retrieve.get_api_services(user=self.request.user)

    def list(self, request):
        queryset = Service.retrieve.get_api_services(user=request.user)
        serializer = ServiceSerializer(queryset, many=True, context={'request': request},
                                       fields=('url', 'name', 'short_description', 'version', 'created', 'updated',
                                               'category', 'jobs')
                                       )
        return Response(serializer.data)

    def retrieve(self, request, api_name=None):
        queryset = Service.retrieve.get_api_services(user=request.user)
        service_tool = get_object_or_404(queryset, api_name=api_name)
        serializer = ServiceSerializer(service_tool, context={'request': request})
        return Response(serializer.data)

    @detail_route(methods=['get'], url_path='jobs')
    def service_job(self, request, api_name=None):
        # RETRIEVE A SERVICE JOB
        queryset = Service.retrieve.get_api_services(request.user)
        service_tool = get_object_or_404(queryset, api_name=api_name)
        queryset_jobs = Job.objects.get_service_job(user=request.user, service=service_tool)
        serializer = JobSerializer(queryset_jobs,
                                   many=True,
                                   context={'request': request},
                                   fields=('url', 'created', 'status', 'service'))
        return Response(serializer.data)

    @detail_route(methods=['get'], url_path="metas")
    def service_metas(self, request, api_name=None):
        queryset = Service.retrieve.get_api_services(request.user)
        service = get_object_or_404(queryset, api_name=api_name)
        serializer = ServiceMetaSerializer(service,
                                           many=False,
                                           context={'request': request})
        return Response(serializer.data)

    @detail_route(methods=['get'], url_path="form")
    def service_form(self, request, api_name=None):
        queryset = Service.retrieve.get_api_services(request.user)
        service_tool = get_object_or_404(queryset, api_name=api_name)
        serializer = ServiceFormSerializer(many=False,
                                           context={'request': request},
                                           instance=service_tool)
        return Response(serializer.data)


class MultipleFieldLookupMixin(object):
    def get_object(self):
        queryset = self.get_queryset()  # Get the base queryset
        queryset = self.filter_queryset(queryset)  # Apply any filter backends
        filter = {}
        for field in self.lookup_fields:
            filter[field] = self.kwargs[field]
        return get_object_or_404(queryset, **filter)  # Lookup the object


class ServiceJobSubmissionView(MultipleFieldLookupMixin, generics.RetrieveAPIView, generics.CreateAPIView,
                               WavesBaseView):
    queryset = ServiceSubmission.objects.all()
    serializer_class = ServiceSubmissionSerializer
    lookup_fields = ('service', 'api_name')

    def get_queryset(self):
        queryset = ServiceSubmission.objects.filter(api_name=self.kwargs.get('api_name'),
                                                    service__api_name=self.kwargs.get('service'),
                                                    available_api=True)
        return queryset

    def get_object(self):
        return get_object_or_404(self.get_queryset())

    def post(self, request, *args, **kwargs):
        # CREATE A NEW JOB
        # print kwargs
        if logger.isEnabledFor(logging.DEBUG):
            for param in request.data:
                logger.debug('param key ' + param)
                logger.debug(request.data[param])
            logger.debug('Request Data %s', request.data)
        service = Service.objects.get(api_name=kwargs['service'])
        # print 'object', self.get_object().__class__
        queryset = ServiceSubmission.objects.get(api_name=kwargs['api_name'],
                                                 service=service)
        service_submission = self.get_object()
        ass_email = request.data.pop('email', None)
        try:
            request.data.pop('api_key')
            submitted_data = {
                'submission': service_submission,
                'client': request.user.pk,
                'inputs': request.data
            }
            serializer = self.get_serializer(context={'request': request},
                                             fields=('inputs',))
            serializer.run_validation(data=submitted_data, )
            job = ServiceJobManager.create_new_job(submission=service_submission,
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


class ServiceJobSubmissionViewForm(ServiceJobSubmissionView):

    def get(self, request, *args, **kwargs):
        submission = self.get_object()
        serializer = ServiceFormSerializer(many=False,
                                           context={'request': request},
                                           instance=submission)
        return Response(serializer.data)
