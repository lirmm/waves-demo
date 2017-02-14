from rest_framework import serializers
from rest_framework.fields import empty
from waves_api.serializers.fields import CommaSeparatedListField, ListElementField, InputFormatField
from waves_api.serializers.dynamic import DynamicFieldsModelSerializer
from waves.models.inputs import *


class BaseParamSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['label', 'name', 'default', 'type', 'mandatory', 'short_description', 'multiple', 'edam_formats',
                  'edam_datas']
        model = BaseParam

    mandatory = serializers.NullBooleanField(source='required')
    short_description = serializers.CharField(source='help_text')
    edam_formats = CommaSeparatedListField()
    edam_datas = CommaSeparatedListField()


class IntegerSerializer(BaseParamSerializer):
    class Meta(BaseParamSerializer.Meta):
        model = IntegerParam


class BooleanSerializer(BaseParamSerializer):
    class Meta(BaseParamSerializer.Meta):
        model = BooleanParam
        fields = BaseParamSerializer.Meta.fields + ['true_value', 'false_value']


class DecimalSerializer(BaseParamSerializer):
    class Meta:
        exclude = ('polymorphic_ctype',)
        model = DecimalParam


class FileSerializer(BaseParamSerializer):
    class Meta(BaseParamSerializer.Meta):
        model = FileInput


class ListSerialzer(BaseParamSerializer):
    class Meta(BaseParamSerializer.Meta):
        model = ListParam
        fields = BaseParamSerializer.Meta.fields + ['values_list']

    values_list = ListElementField(source='list_elements')


class InputSerializer(DynamicFieldsModelSerializer):
    """ Serialize JobInput """

    class Meta:
        model = BaseParam
        queryset = BaseParam.objects.all()
        exclude = ('polymorphic_ctype',)
        fields = ('label', 'name', 'default', 'type', 'cmd_format', 'mandatory', 'help_text', 'multiple')
        extra_kwargs = {
            'url': {'view_name': 'waves-waves_api:waves-services-detail', 'lookup_field': 'api_name'}
        }

    cmd_format = InputFormatField()

    def __init__(self, instance=None, data=empty, **kwargs):
        super(InputSerializer, self).__init__(instance, data, **kwargs)

    def to_representation(self, obj):
        """ Return representation for an Input, including dependents inputs if needed """
        if isinstance(obj, FileInput):
            return FileSerializer(obj, context=self.context).to_representation(obj)
        elif isinstance(obj, ListParam):
            return ListSerialzer(obj, context=self.context).to_representation(obj)
        elif isinstance(obj, BooleanParam):
            return BooleanSerializer(obj, context=self.context).to_representation(obj)
        elif isinstance(obj, IntegerParam):
            return IntegerSerializer(obj, context=self.context).to_representation(obj)
        elif isinstance(obj, DecimalParam):
            return DecimalSerializer(obj, context=self.context).to_representation(obj)
        else:
            return BaseParamSerializer(obj, context=self.context).to_representation(obj)

        """
        if instance.dependents_inputs.count() > 0:
            representation = ConditionalInputSerializer(instance, context=self.context).to_representation(instance)
        else:
            representation = super(InputSerializer, self).to_representation(instance)
        return representation
        """


class RelatedInputSerializer(InputSerializer):
    """ Serialize a dependent Input (RelatedParam models) """

    class Meta:
        model = RelatedParam
        fields = InputSerializer.Meta.fields

    def to_representation(self, instance):
        """ Return representation of a Related Input """
        initial_repr = super(RelatedInputSerializer, self).to_representation(instance)
        return {instance.when_value: initial_repr}


class ConditionalInputSerializer(serializers.ModelSerializer):
    """ Serialize inputs if it's a conditional one """

    class Meta:
        model = BaseParam
        fields = ('label', 'name', 'default', 'type', 'cmd_format', 'mandatory', 'short_description', 'description',
                  'multiple', 'when')

    when = RelatedInputSerializer(source='dependents_inputs', many=True, read_only=True)
    format = InputFormatField()
