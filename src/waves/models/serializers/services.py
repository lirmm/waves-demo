"""WAVES models export module for Services """
from __future__ import unicode_literals

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from rest_framework import serializers as rest_serializer

import waves.settings
from waves.api.v2.serializers.dynamic import DynamicFieldsModelSerializer
from waves.api.v2.serializers import ServiceSerializer as BaseServiceSerializer, \
    ServiceSubmissionSerializer as BaseServiceSubmissionSerializer
from waves.models import *
from waves.models.serializers.base import RelatedSerializerMixin
from waves.models.serializers.categories import CategorySerializer
from waves.models.serializers.runners import RunnerSerializer, RunnerParamSerializer

__all__ = ['ServiceMetaSerializer', 'ServiceSubmissionSerializer', 'ExitCodeSerializer', 'ServiceSerializer']


class ServiceMetaSerializer(rest_serializer.ModelSerializer):
    class Meta:
        model = ServiceMeta
        fields = ('type', 'title', 'value', 'is_url', 'order')


class RelatedInputSerializer(rest_serializer.ModelSerializer):
    """ Serialize a RelatedParam """

    class Meta:
        model = RelatedParam
        fields = ('order', 'label', 'name', 'default', 'type', 'param_type', 'format', 'mandatory', 'multiple',
                  'display', 'description', 'short_description', 'when_value')


class ServiceInputSerializer(DynamicFieldsModelSerializer, RelatedSerializerMixin):
    """ Serialize a basic service input with its dependents parameters"""

    class Meta:
        model = AParam
        fields = ('order', 'label', 'name', 'default', 'type', 'param_type', 'format',
                  'mandatory', 'multiple', 'display', 'description', 'short_description',
                  'dependents_inputs')

    dependent_inputs = RelatedInputSerializer(many=True, required=False)

    def create(self, validated_data):
        dependent_inputs = validated_data.pop('dependents_inputs')
        srv_input = AParam.objects.create(**validated_data)
        self.create_related(foreign={'parent': srv_input},
                            serializer=RelatedInputSerializer,
                            datas=dependent_inputs)
        return srv_input


class ServiceSubmissionSerializer(BaseServiceSubmissionSerializer, RelatedSerializerMixin):
    """ Service Submission export / import """

    class Meta:
        model = Submission
        fields = ('api_name', 'order', 'name', 'available_online', 'available_api', 'all_inputs',
                  'submission_inputs')

    export_submission_inputs = ServiceInputSerializer(many=True, required=False)
    submission_inputs = ServiceInputSerializer(many=True, required=False, write_only=True, source="all_inputs")

    def create(self, validated_data):
        submission_inputs = validated_data.pop('export_submission_inputs')
        # validated_data['api_name'] = validated_data.get('service').api_name
        submission = Submission.objects.create(**validated_data)
        self.create_related(foreign={'service': submission}, serializer=ServiceInputSerializer, datas=submission_inputs)
        return submission


class ExitCodeSerializer(rest_serializer.ModelSerializer):
    """ ExitCode export / import """

    class Meta:
        model = SubmissionExitCode
        fields = ('exit_code', 'message')


class SubmissionOutputSerializer(rest_serializer.ModelSerializer):
    class Meta:
        model = Submission
        fields = ('api_name',)

    def create(self, validated_data):
        return Submission(api_name=validated_data.get('api_name'))


class ServiceOutputSerializer(rest_serializer.ModelSerializer):
    class Meta:
        model = SubmissionOutput
        fields = ('order', 'name', 'from_input', 'description',
                  'short_description', 'from_input', 'file_pattern')

    def create(self, validated_data):
        # retrieve related input
        submission_from = validated_data.pop('from_input_submission')
        service = validated_data['service']
        obj = super(ServiceOutputSerializer, self).create(validated_data)
        for sub in submission_from:
            submit = service.submissions.filter(api_name=sub['submission']['api_name']).first()
            srv_input = submit.submission_inputs.filter(name=sub['srv_input']['name']).first()
            output_submission = SubmissionOutput.objects.create(srv_input=srv_input,
                                                                submission=submit,
                                                                srv_output=obj)
            obj.from_input_submission.add(output_submission)
        return obj


class ServiceTmpSerializer(rest_serializer.ModelSerializer):
    class Meta:
        model = Service
        fields = ('name',)


class ServiceRunnerParamSerializer(rest_serializer.ModelSerializer):
    class Meta:
        model = SubmissionRunParam
        fields = ('param', '_value', 'service')

    param = RunnerParamSerializer(many=False, required=False)
    service = ServiceTmpSerializer(required=False)

    def create(self, validated_data):
        service = validated_data['service']
        param_dict = validated_data.pop('param')
        value = validated_data.pop('_value')
        param = service.runner.runner_run_params.get(name=param_dict['name'])
        obj, created = SubmissionRunParam.objects.update_or_create(defaults={'_value': value},
                                                                   param=param, service=service)
        return obj


class ServiceSerializer(BaseServiceSerializer, RelatedSerializerMixin):
    """ Service export / import """

    class Meta:
        model = Service
        fields = ('db_version', 'name', 'version', 'description', 'short_description', 'metas', 'runner', 'category',
                  'srv_run_params', 'submissions', 'service_outputs', 'exit_codes')

    db_version = rest_serializer.SerializerMethodField()
    metas = ServiceMetaSerializer(many=True, required=False)
    submissions = ServiceSubmissionSerializer(many=True, required=False)
    exit_codes = ExitCodeSerializer(many=True, required=False)
    service_outputs = ServiceOutputSerializer(many=True, required=False)
    runner = RunnerSerializer(many=False, required=False)
    category = CategorySerializer(many=False, required=False, validators=[])
    srv_run_params = ServiceRunnerParamSerializer(many=True, required=False)

    def __init__(self, *args, **kwargs):
        self.skip_category = kwargs.pop('skip_cat', False)
        self.skip_runner = kwargs.pop('skip_run', False)
        super(ServiceSerializer, self).__init__(*args, **kwargs)

    @transaction.atomic
    def create(self, validated_data):
        """ Create a new service from submitted data"""
        metas_srv = validated_data.pop('metas')
        submissions = validated_data.pop('submissions')
        outputs = validated_data.pop('service_outputs')
        ext_codes = validated_data.pop('exit_codes')
        runner = validated_data.pop('runner')
        category = validated_data.pop('category')
        srv_run_params = validated_data.pop('srv_run_params')
        if not self.skip_runner:
            try:
                run_on = Runner.objects.filter(clazz=runner['clazz']).first()
            except ObjectDoesNotExist:
                srv = RunnerSerializer(data=runner)
                if srv.is_valid():
                    run_on = srv.save()
                else:
                    run_on = None
        else:
            run_on = None
        srv_object = Service.objects.create(**validated_data)
        srv_object.runner = run_on
        if not self.skip_category:
            cat = CategorySerializer(data=category, many=False)
            if cat.is_valid():
                srv_object.category = cat.save()
        srv_object.save()
        if not self.skip_runner:
            s_run_p = ServiceRunnerParamSerializer(data=srv_run_params, many=True)
            if s_run_p.is_valid():
                s_run_p.save(service=srv_object)
        srv_object.metas = self.create_related(foreign={'service': srv_object}, serializer=ServiceMetaSerializer,
                                               datas=metas_srv)
        srv_object.submissions = self.create_related(foreign={'service': srv_object},
                                                     serializer=ServiceSubmissionSerializer, datas=submissions)
        srv_object.service_outputs = self.create_related(foreign={'service': srv_object},
                                                         serializer=ServiceOutputSerializer, datas=outputs)
        srv_object.exit_codes = self.create_related(foreign={'service': srv_object},
                                                    serializer=ExitCodeSerializer, datas=ext_codes)
        return srv_object
