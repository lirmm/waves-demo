# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.reverse import reverse as reverse_drf

from dynamic import DynamicFieldsModelSerializer
from waves.models import Service, JobHistory, JobInput, Job, JobOutput

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
        fields = ('name', 'input', 'value')
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
        fields = ('name', 'download_url', 'content')

    download_url = serializers.SerializerMethodField()
    # content = serializers.SerializerMethodField()

    def file_get_content(self, instance):
        from os.path import getsize
        if getsize(instance.file_path) < 500:
            with open(instance.file_path) as fp:
                file_content = fp.read()
            return file_content.decode('utf-8')
        return "Content length exceeded, please download"

    def to_representation(self, instance):
        from waves.utils import normalize_value
        to_repr = {}
        for output in instance:
            to_repr[normalize_value(output.name)] = {
                "label": output.name,
                "download_uri": self.get_download_url(output),
                "content": self.file_get_content(output)
            }
        return to_repr

    def get_download_url(self, obj):
        return "%s?export=1" % reverse_drf(viewname='waves:job-api-output', request=self.context['request'],
                                           kwargs={'slug': obj.slug})


class JobOutputDetailSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Job
        fields = ('url', 'status_txt', 'status_code', 'outputs')
        extra_kwargs = {
            'url': {'view_name': 'waves:waves-jobs-detail', 'lookup_field': 'slug'}
        }

    status_txt = serializers.SerializerMethodField()
    status_code = serializers.IntegerField(source='status')
    outputs = JobOutputSerializer(read_only=True, source='output_files_exists')

    @staticmethod
    def get_status_txt(obj):
        return obj.get_status_display()


class JobSerializer(serializers.HyperlinkedModelSerializer, DynamicFieldsModelSerializer):
    class Meta:
        model = Job
        fields = ('url', 'title', 'slug', 'status_code', 'status_txt', 'created', 'updated', 'inputs', 'outputs',
                  'history', 'client', 'service',)
        readonly_fields = (
            'status_code', 'status_txt', 'slug', 'client', 'service', 'created', 'updated', 'url', 'history')
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
        return reverse_drf(viewname='waves:waves-jobs-history', request=self.context['request'],
                           kwargs={'slug': obj.slug})

    def get_outputs(self, obj):
        return reverse_drf(viewname='waves:waves-jobs-outputs', request=self.context['request'],
                           kwargs={'slug': obj.slug})

    def get_inputs(self, obj):
        return reverse_drf(viewname='waves:waves-jobs-inputs', request=self.context['request'],
                           kwargs={'slug': obj.slug})

    @staticmethod
    def get_status_txt(job):
        return job.get_status_display()
