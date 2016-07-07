from __future__ import unicode_literals
from rest_framework import serializers
from rest_framework.fields import empty

from dynamic import DynamicFieldsModelSerializer
from waves.models import ServiceInput, ServiceOutput, ServiceMeta, Service, RelatedInput


class InputSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = ServiceInput
        fields = ('label', 'name', 'default', 'type', 'format', 'mandatory', 'description', 'multiple')
        extra_kwargs = {
            'url': {'view_name': 'servicetoolinput-detail', 'lookup_field': 'api_name'}
        }

    def __init__(self, instance=None, data=empty, **kwargs):
        super(InputSerializer, self).__init__(instance, data, **kwargs)

    def build_field(self, field_name, info, model_class, nested_depth):
        return super(InputSerializer, self).build_field(field_name, info, model_class, nested_depth)

    def to_representation(self, instance):
        if hasattr(instance, 'when_value'):
            representation = super(RelatedInputSerializer, self).to_representation(instance)
        elif instance.dependent_inputs.count() > 0:
            representation = ConditionalInputSerializer(instance, context=self.context).to_representation(instance)
        else:
            representation = super(InputSerializer, self).to_representation(instance)
        return representation


class RelatedInputSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = RelatedInput
        fields = ('label', 'name', 'default', 'type', 'format', 'mandatory', 'description', 'multiple')

    def to_representation(self, instance):
        initial_repr = super(RelatedInputSerializer, self).to_representation(instance)
        return {
            instance.when_value: initial_repr
        }


class ConditionalInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceInput
        fields = ('label', 'name', 'default', 'type', 'format', 'mandatory', 'description', 'multiple', 'when')

    when = RelatedInputSerializer(source='dependent_inputs', many=True, read_only=True)


class OutputSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = ServiceOutput
        exclude = ('order', 'id', 'service', 'from_input')


class MetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceMeta
        exclude = ('id', 'order', 'service')


class ServiceSerializer(serializers.HyperlinkedModelSerializer, DynamicFieldsModelSerializer):
    class Meta:
        model = Service
        fields = ('url', 'id', 'category', 'name', 'version', 'created', 'description', 'metas',
                  'inputs', 'outputs')
        lookup_field = 'api_name'
        extra_kwargs = {
            'url': {'view_name': 'servicetool-detail', 'lookup_field': 'api_name'}
        }

    metas = MetaSerializer(many=True,
                           read_only=True)
    inputs = InputSerializer(many=True,
                             read_only=True,
                             source='base_inputs')
    outputs = OutputSerializer(many=True,
                               read_only=True)
    category = serializers.HyperlinkedRelatedField(many=False,
                                                   read_only=True,
                                                   view_name='servicetoolcategory-detail',
                                                   lookup_field='name')
