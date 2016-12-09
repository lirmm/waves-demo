"""WAVES models export module for Services """
from __future__ import unicode_literals

from django.db import transaction
from rest_framework import serializers
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ValidationError
import waves.settings
from waves.api.serializers.dynamic import DynamicFieldsModelSerializer
from waves.api.serializers.services import ServiceSerializer as BaseServiceSerializer, \
    ServiceSubmissionSerializer as BaseServiceSubmissionSerializer
from waves.models.serializers import RelatedSerializerMixin
from .runners import RunnerSerializer, RunnerParamSerializer
from .categories import CategorySerializer
from waves.models.services import Service, ServiceMeta, ServiceExitCode, ServiceRunnerParam
from waves.models.runners import Runner
from waves.models.submissions import ServiceSubmission, ServiceInput, RelatedInput, ServiceOutput

__all__ = ['ServiceMetaSerializer', 'ServiceSubmissionSerializer', 'ExitCodeSerializer', 'ServiceSerializer']


class ServiceMetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceMeta
        fields = ('type', 'title', 'value', 'is_url', 'order')


class RelatedInputSerializer(serializers.ModelSerializer):
    """ Serialize a RelatedInput """

    class Meta:
        model = RelatedInput
        fields = ('order', 'label', 'name', 'default', 'type', 'param_type', 'format',
                  'mandatory', 'multiple', 'editable', 'display', 'description', 'short_description',
                  'when_value')


class ServiceInputSerializer(DynamicFieldsModelSerializer, RelatedSerializerMixin):
    """ Serialize a basic service input with its dependents parameters"""

    class Meta:
        model = ServiceInput
        fields = ('order', 'label', 'name', 'default', 'type', 'param_type', 'format',
                  'mandatory', 'multiple', 'editable', 'display', 'description', 'short_description',
                  'dependent_inputs')

    dependent_inputs = RelatedInputSerializer(many=True, required=False)

    def create(self, validated_data):
        dependent_inputs = validated_data.pop('dependent_inputs')
        srv_input = ServiceInput.objects.create(**validated_data)
        self.create_related(foreign={'related_to': srv_input},
                            serializer=RelatedInputSerializer,
                            datas=dependent_inputs)
        return srv_input


class ServiceSubmissionSerializer(BaseServiceSubmissionSerializer, RelatedSerializerMixin):
    """ Service Submission export / import """

    class Meta:
        model = ServiceSubmission
        fields = ('api_name', 'order', 'label', 'available_online', 'available_api', 'export_service_inputs',
                  'service_inputs')

    export_service_inputs = ServiceInputSerializer(many=True, required=False)
    service_inputs = ServiceInputSerializer(many=True, required=False, write_only=True, source="export_service_inputs")

    def create(self, validated_data):
        service_inputs = validated_data.pop('export_service_inputs')
        # validated_data['api_name'] = validated_data.get('service').api_name
        submission = ServiceSubmission.objects.create(**validated_data)
        self.create_related(foreign={'service': submission}, serializer=ServiceInputSerializer, datas=service_inputs)
        return submission


class ExitCodeSerializer(serializers.ModelSerializer):
    """ ExitCode export / import """

    class Meta:
        model = ServiceExitCode
        fields = ('exit_code', 'message')


class SubmissionOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceSubmission
        fields = ('api_name',)

    def create(self, validated_data):
        return ServiceSubmission(api_name=validated_data.get('api_name'))


class ServiceOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceOutput
        fields = ('order', 'name', 'related_from_input', 'ext', 'may_be_empty', 'description',
                  'short_description', 'from_input', 'file_pattern')

    def create(self, validated_data):
        # retrieve related input
        submission_from = validated_data.pop('from_input_submission')
        service = validated_data['service']
        obj = super(ServiceOutputSerializer, self).create(validated_data)
        for sub in submission_from:
            submit = service.submissions.filter(api_name=sub['submission']['api_name']).first()
            srv_input = submit.service_inputs.filter(name=sub['srv_input']['name']).first()
            output_submission = ServiceOutputFromInputSubmission.objects.create(srv_input=srv_input,
                                                                                submission=submit,
                                                                                srv_output=obj)
            obj.from_input_submission.add(output_submission)
        return obj


class ServiceTmpSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ('name',)


class ServiceRunnerParamSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceRunnerParam
        fields = ('param', '_value', 'service')

    param = RunnerParamSerializer(many=False, required=False)
    service = ServiceTmpSerializer(required=False)

    def create(self, validated_data):
        service = validated_data['service']
        param_dict = validated_data.pop('param')
        value = validated_data.pop('_value')
        param = service.run_on.runner_params.get(name=param_dict['name'])
        obj, created = ServiceRunnerParam.objects.update_or_create(defaults={'_value': value},
                                                                   param=param, service=service)
        return obj


class ServiceSerializer(BaseServiceSerializer, RelatedSerializerMixin):
    """ Service export / import """

    class Meta:
        model = Service
        fields = ('db_version', 'name', 'version', 'description', 'short_description', 'metas', 'run_on', 'category',
                  'service_run_params', 'submissions', 'service_outputs', 'service_exit_codes')

    db_version = serializers.SerializerMethodField()
    metas = ServiceMetaSerializer(many=True, required=False)
    submissions = ServiceSubmissionSerializer(many=True, required=False)
    service_exit_codes = ExitCodeSerializer(many=True, required=False)
    service_outputs = ServiceOutputSerializer(many=True, required=False)
    run_on = RunnerSerializer(many=False, required=False)
    category = CategorySerializer(many=False, required=False, validators=[])
    service_run_params = ServiceRunnerParamSerializer(many=True, required=False)

    def get_db_version(self, obj):
        return waves.settings.WAVES_DB_VERSION

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
        ext_codes = validated_data.pop('service_exit_codes')
        runner = validated_data.pop('run_on')
        category = validated_data.pop('category')
        srv_run_params = validated_data.pop('service_run_params')
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
        srv_object.run_on = run_on
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
        srv_object.service_exit_codes = self.create_related(foreign={'service': srv_object},
                                                            serializer=ExitCodeSerializer, datas=ext_codes)
        return srv_object
