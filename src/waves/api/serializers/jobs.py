from __future__ import unicode_literals

import logging

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from rest_framework import serializers

from dynamic import DynamicFieldsModelSerializer
from waves.api.serializers.services import ServiceSerializer, InputSerializer
from waves.models import Service, JobHistory, JobInput, Job, JobOutput
from waves.utils import get_complete_absolute_url
logger = logging.getLogger(__name__)
User = get_user_model()


class StatusSerializer(serializers.Serializer):

    status_code = serializers.IntegerField(source='status')
    status_txt = serializers.SerializerMethodField()

    def __init__(self, instance=None, **kwargs):
        super(StatusSerializer, self).__init__(instance, **kwargs)
        self.status_code = instance.status

    @staticmethod
    def get_status_txt(obj):
        return obj.get_status_display()


class JobHistorySerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = JobHistory
        fields = ('status_txt', 'status_code', 'timestamp', 'message')

    status_txt = serializers.SerializerMethodField()
    status_code = serializers.IntegerField(source='status')

    @staticmethod
    def get_status_txt(history):
        return history.get_status_display()


class JobHistoryDetailSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Job
        fields = ('url', 'last_status', 'last_status_txt', 'job_history')
        extra_kwargs = {
            'url': {'view_name': 'waves:waves-jobs-detail', 'lookup_field': 'slug'}
        }
    last_status = serializers.IntegerField(source='status')
    last_status_txt = serializers.SerializerMethodField()
    job_history = JobHistorySerializer(many=True, read_only=True)

    @staticmethod
    def get_last_status_txt(obj):
        return obj.get_status_display()


class JobInputSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = JobInput
        fields = ('name', 'input', 'value' )
        depth = 1

    def __init__(self, *args, **kwargs):
        super(JobInputSerializer, self).__init__(*args, **kwargs)

    input = serializers.SerializerMethodField()

    def get_input(self, obj):
        return obj.srv_input.label


class JobInputDetailSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Job
        fields = ('url', 'status', 'inputs')
        extra_kwargs = {
            'url': {'view_name': 'waves:waves-jobs-detail', 'lookup_field': 'slug'}
        }
    status = serializers.SerializerMethodField()
    inputs = JobInputSerializer(source='job_inputs', many=True, read_only=True)

    @staticmethod
    def get_status(obj):
        return obj.get_status_display()


class JobOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobOutput
        fields = ('name', 'download_url')
    download_url = serializers.SerializerMethodField()

    def to_representation(self, instance):
        from waves.utils import normalize_output
        to_repr = {}
        for output in instance:
            to_repr[normalize_output(output.name)] = {
                "label": output.name,
                "download_uri": get_complete_absolute_url(output.download_url)
            }
        return to_repr

    @staticmethod
    def get_download_url(obj):
        return get_complete_absolute_url("%s?export=1" % reverse('waves:job_api_output', kwargs={'slug': obj.slug}))


class JobOutputDetailSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Job
        fields = ('url', 'status', 'outputs')
        extra_kwargs = {
            'url': {'view_name': 'waves:waves-jobs-detail', 'lookup_field': 'slug'}
        }
    status = serializers.SerializerMethodField()
    outputs = JobOutputSerializer(read_only=True, source='output_files_exists')

    @staticmethod
    def get_status(obj):
        return obj.get_status_display()


class JobSerializer(serializers.HyperlinkedModelSerializer, DynamicFieldsModelSerializer):
    class Meta:
        model = Job
        fields = ('url', 'slug', 'status_code', 'status_txt', 'created', 'updated', 'inputs', 'outputs',
                  'history', 'client', 'service',)
        readonly_fields = ('status_code', 'status_txt', 'slug', 'client', 'service', 'created', 'updated', 'url', 'history')
        extra_kwargs = {
            'url': {'view_name': 'waves:waves-jobs-detail', 'lookup_field': 'slug'}
        }
        depth = 1
        lookup_field = 'slug'

    status_txt = serializers.SerializerMethodField()
    status_code = serializers.IntegerField(source='status')
    client = serializers.StringRelatedField(many=False, read_only=False)
    service = serializers.HyperlinkedRelatedField(many=False, read_only=False,
                                                  view_name='waves:waves-services-detail',
                                                  lookup_field='api_name',
                                                  queryset=Service.objects.all(),
                                                  required=True)
    history = serializers.SerializerMethodField()
    outputs = serializers.SerializerMethodField()
    inputs = serializers.SerializerMethodField()

    def get_history(self, obj):
        return 'http://%s%s' % (
            Site.objects.get_current().domain, reverse('waves:waves-jobs-history', kwargs={'slug': obj.slug}))

    def get_outputs(self, obj):
        return 'http://%s%s' % (
            Site.objects.get_current().domain, reverse('waves:waves-jobs-outputs', kwargs={'slug': obj.slug}))

    def get_inputs(self, obj):
        return 'http://%s%s' % (
            Site.objects.get_current().domain, reverse('waves:waves-jobs-inputs', kwargs={'slug': obj.slug}))

    @staticmethod
    def get_status_txt(job):
        return job.get_status_display()
