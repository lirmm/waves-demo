# -*- coding: utf-8 -*-
""" Jobs API serializers """
from __future__ import unicode_literals

import logging
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.reverse import reverse
from dynamic import DynamicFieldsModelSerializer
from waves.models import Service, JobHistory, JobInput, Job, JobOutput

logger = logging.getLogger(__name__)
User = get_user_model()


class JobHistorySerializer(DynamicFieldsModelSerializer):
    """ JobHistory Serializer - display status / message / timestamp """
    class Meta:
        model = JobHistory
        fields = ('status_txt', 'status_code', 'timestamp', 'message')
    status_txt = serializers.SerializerMethodField()
    status_code = serializers.IntegerField(source='status')

    @staticmethod
    def get_status_txt(history):
        """ return status text """
        return history.get_status_display()


class JobHistoryDetailSerializer(serializers.HyperlinkedModelSerializer):
    """ Job history serializer """
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
        """ return status text """
        return obj.get_status_display()


class JobInputSerializer(DynamicFieldsModelSerializer):
    """ JobInput serializer """
    class Meta:
        model = JobInput
        fields = ('name', 'label', 'value')
        # depth = 1
    # input = serializers.SerializerMethodField()

    def get_input(self, obj):
        """ Return input label """
        return obj.label


class JobInputDetailSerializer(serializers.HyperlinkedModelSerializer):
    """ Job Input Details serializer """
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
        """ return job status """
        return obj.get_status_display()


class JobOutputSerializer(serializers.ModelSerializer):
    """ JobOutput serializer """
    class Meta:
        model = JobOutput
        fields = ('name', 'download_url', 'content')
    download_url = serializers.SerializerMethodField()

    def file_get_content(self, instance):
        """ Either returns output content, or text of content size exceeds 500ko"""
        from os.path import getsize
        if getsize(instance.file_path) < 500:
            with open(instance.file_path) as fp:
                file_content = fp.read()
            return file_content.decode()
        return "Content length exceeded, please download"

    def to_representation(self, instance):
        """ Representation for a output """
        from waves.utils.normalize import normalize_value
        to_repr = {}
        for output in instance:
            to_repr[normalize_value(output.name)] = {
                "label": output.name,
                "download_uri": self.get_download_url(output),
                "content": self.file_get_content(output)
            }
        return to_repr

    def get_download_url(self, obj):
        """ Link to jobOutput download uri """
        return "%s?export=1" % reverse(viewname='waves:job-api-output', request=self.context['request'],
                                       kwargs={'slug': obj.slug})


class JobOutputDetailSerializer(serializers.HyperlinkedModelSerializer):
    """ JobOutput List serializer """
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
        """ Return job status text """
        return obj.get_status_display()


class JobSerializer(DynamicFieldsModelSerializer, serializers.HyperlinkedModelSerializer):
    """ Serializer for Job (only GET) """
    class Meta:
        model = Job
        fields = ('url', 'title', 'status_code', 'status_txt', 'created', 'updated', 'inputs', 'outputs',
                  'history', 'client', 'service', 'slug')
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
    service = serializers.HyperlinkedRelatedField(many=False, read_only=False, view_name='waves:waves-services-detail',
                                                  lookup_field='api_name', queryset=Service.objects.all(),
                                                  required=True)
    history = serializers.SerializerMethodField()
    outputs = serializers.SerializerMethodField()
    inputs = serializers.SerializerMethodField()

    def get_history(self, obj):
        """ Link to job history details api endpoint """
        return reverse(viewname='waves:waves-jobs-history', request=self.context['request'],
                       kwargs={'slug': obj.slug})

    def get_outputs(self, obj):
        """ Link to job outputs api endpoint """
        return reverse(viewname='waves:waves-jobs-outputs', request=self.context['request'],
                       kwargs={'slug': obj.slug})

    def get_inputs(self, obj):
        """ Link to job inputs api endpoint """
        return reverse(viewname='waves:waves-jobs-inputs', request=self.context['request'],
                       kwargs={'slug': obj.slug})

    @staticmethod
    def get_status_txt(job):
        """ Return string corresponding to status code """
        return job.get_status_display()


class JobCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ('job_inputs', 'submission')
        write_only_fields = ('job_inputs',)

    def create(self, validated_data):
        print 'in create', validated_data
        return Job.objects.create()
