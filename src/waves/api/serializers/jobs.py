from __future__ import unicode_literals

import logging

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from rest_framework import serializers

from dynamic import DynamicFieldsModelSerializer
from waves.api.serializers.services import ServiceSerializer, InputSerializer
from waves.models import Service, JobHistory, JobInput, Job

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
        fields = ('name', 'value', 'type', 'param_type', 'srv_input')
        depth = 1

    def __init__(self, *args, **kwargs):
        super(JobInputSerializer, self).__init__(*args, **kwargs)

    srv_input = InputSerializer()


class JobSerializer(serializers.HyperlinkedModelSerializer, DynamicFieldsModelSerializer):
    class Meta:
        model = Job
        fields = ('url', 'created', 'slug', 'status', 'job_inputs',
                  'job_outputs', 'client', 'service', 'job_history', 'full_history')
        readonly_fields = ('status', 'slug', 'job_history', 'job_outputs')
        extra_kwargs = {
            'url': {'view_name': 'waves-jobs-detail', 'lookup_field': 'slug'}
        }
        depth = 1
        lookup_field = 'slug'

    status = serializers.SerializerMethodField()
    client = serializers.StringRelatedField(many=False, read_only=False)
    service = serializers.HyperlinkedRelatedField(many=False, read_only=False,
                                                  view_name='waves-services-detail',
                                                  lookup_field='api_name',
                                                  queryset=Service.objects.all(),
                                                  required=True)
    job_history = JobHistorySerializer(many=True, read_only=True)
    job_outputs = serializers.StringRelatedField(many=True, read_only=True)
    job_inputs = JobInputSerializer(many=True, read_only=False,
                                    fields=('name', 'label', 'value'))

    full_history = serializers.SerializerMethodField()

    def get_full_history(self, obj):
        return '%s%s' % (
            Site.objects.get_current().domain, reverse('waves-jobs-history', kwargs={'slug': obj.slug}))


    @staticmethod
    def get_status(job):
        return job.get_status_display()
