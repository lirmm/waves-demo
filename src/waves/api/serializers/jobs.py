from __future__ import unicode_literals
import logging

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from dynamic import DynamicFieldsModelSerializer

from waves.models import Service, JobHistory, JobInput, Job
from waves.utils import log_func_details
from waves.api.serializers.services import ServiceSerializer

logger = logging.getLogger(__name__)
User = get_user_model()


class JobHistorySerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = JobHistory
        fields = ('timestamp', 'status', 'message')

    status = serializers.SerializerMethodField()

    @staticmethod
    def get_status(history):
        return history.get_status_display()


class JobInputSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = JobInput
        fields = ('name', 'value')
        depth = 1


class JobSerializer(serializers.HyperlinkedModelSerializer, DynamicFieldsModelSerializer):
    class Meta:
        model = Job
        fields = ('url', 'created', 'slug', 'status', 'job_history', 'job_inputs',
                  'job_outputs', 'client', 'service')
        readonly_fields = ('status', 'slug', 'job_history', 'job_outputs')
        extra_kwargs = {
            'url': {'view_name': 'servicejob-detail', 'lookup_field': 'slug'}
        }
        depth = 1
        lookup_field = 'slug'

    status = serializers.SerializerMethodField()
    client = serializers.StringRelatedField(many=False, read_only=False)
    service = serializers.HyperlinkedRelatedField(many=False, read_only=False,
                                                  view_name='servicetool-detail',
                                                  lookup_field='api_name',
                                                  queryset=Service.objects.all(),
                                                  required=True)
    job_history = JobHistorySerializer(many=True, read_only=True)
    job_outputs = serializers.StringRelatedField(many=True, read_only=True)
    job_inputs = JobInputSerializer(many=True, read_only=False)

    @staticmethod
    def get_status(job):
        return job.get_status_display()

    @log_func_details
    def save(self, **kwargs):
        return super(JobSerializer, self).save(**kwargs)

    @log_func_details
    def is_valid(self, raise_exception=False):
        logger.debug('initial %s', self.initial_data['service'])
        # TODO add service input validation
        self.initial_data['service'] = ServiceSerializer(data={'service': self.initial_data['service']})
        return super(JobSerializer, self).is_valid(raise_exception)

    @log_func_details
    def create(self, validated_data):
        logger.debug("Validated data %s", validated_data)
        logger.debug("Initial ? %s", self.initial_data)
        service_obj = Service.objects.get(pk=validated_data['service'])
        try:
            ass_email = validated_data['email']
        except KeyError:
            ass_email = self.request.user.email
            pass

        job = Service.objects.create_new_job(service=service_obj,
                                             email_to=ass_email,
                                             submitted_inputs=validated_data,
                                             user=self.request.user if self.request.user.is_authenticated() else None)
        logger.debug('Current service job submission ' + service_obj.name)
        for job_input in job.job_inputs:
            logger.debug(job_input.name)
            logger.debug(job_input.value)
        logger.debug("******************* /////////// serializer create *********************")
        return job


class ServiceJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ('client', 'service')

    @log_func_details
    def is_valid(self, raise_exception=False):
        logger.debug('ServiceJobSerializer initial %s', self.initial_data)
        return super(ServiceJobSerializer, self).is_valid(raise_exception)

    @log_func_details
    def create(self, validated_data):

        client = validated_data.pop('client')
        service = validated_data.pop('service')
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("******************* serializer create ****************")
            logger.debug("Validated data %s", validated_data)
            logger.debug('Initial data %s', self.initial_data)
            logger.debug('Submitted inputs %s', validated_data)
            logger.debug('Service %s', service)
            logger.debug('Client %s', client)
        try:
            ass_email = validated_data['email']
        except KeyError:
            ass_email = None
            pass
        # service = Service.objects.get(pk=)
        self.instance = Service.objects.create_new_job(service=service,
                                                       email_to=ass_email,
                                                       submitted_inputs=self.initial_data,
                                                       user=client)
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug('Current service job submission ' + self.instance.title)
            for job_input in self.instance.job_inputs.all():
                logger.debug(job_input.name)
                logger.debug(job_input.value)
            logger.debug("******************* /////////// serializer create *********************")
        return self.instance
