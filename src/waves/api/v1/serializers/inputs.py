from rest_framework import serializers
from rest_framework.fields import empty
from .fields import CommaSeparatedListField, ListElementField, InputFormatField
from .dynamic import DynamicFieldsModelSerializer
from waves.models.inputs import *


class AParamSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['label', 'name', 'default', 'type', 'mandatory', 'description', 'multiple', 'edam_formats',
                  'edam_datas']
        model = AParam

    mandatory = serializers.NullBooleanField(source='required')
    description = serializers.CharField(source='help_text')
    edam_formats = CommaSeparatedListField()
    edam_datas = CommaSeparatedListField()

    @staticmethod
    def get_type(param):
        return param.type


class IntegerSerializer(AParamSerializer):
    class Meta(AParamSerializer.Meta):
        model = IntegerParam
        fields = AParamSerializer.Meta.fields + ['min_val', 'max_val']

    default = serializers.IntegerField()
    min_val = serializers.IntegerField()
    max_val = serializers.IntegerField()


class BooleanSerializer(AParamSerializer):
    class Meta(AParamSerializer.Meta):
        model = BooleanParam
        fields = AParamSerializer.Meta.fields + ['true_value', 'false_value']


class DecimalSerializer(AParamSerializer):
    class Meta:
        model = DecimalParam
        fields = AParamSerializer.Meta.fields + ['min_val', 'max_val']

    default = serializers.DecimalField(decimal_places=3, max_digits=50, coerce_to_string=False)
    min_val = serializers.DecimalField(decimal_places=3, max_digits=50, coerce_to_string=False)
    max_val = serializers.DecimalField(decimal_places=3, max_digits=50, coerce_to_string=False)


class FileSerializer(AParamSerializer):
    class Meta(AParamSerializer.Meta):
        model = FileInput
        fields = AParamSerializer.Meta.fields + ['max_size', 'allowed_extensions']


class ListSerialzer(AParamSerializer):
    class Meta(AParamSerializer.Meta):
        model = ListParam
        fields = AParamSerializer.Meta.fields + ['values_list']

    values_list = ListElementField(source='list_elements')


class InputSerializer(DynamicFieldsModelSerializer):
    """ Serialize JobInput """

    class Meta:
        model = AParam
        queryset = AParam.objects.all()
        fields = ('label', 'name', 'default', 'type', 'mandatory', 'description', 'multiple')
        extra_kwargs = {
            'url': {'view_name': 'waves_api:waves-services-detail', 'lookup_field': 'api_name'}
        }

    description = serializers.CharField(source='help_text')

    def __init__(self, instance=None, data=empty, **kwargs):
        super(InputSerializer, self).__init__(instance, data, **kwargs)

    def to_representation(self, obj):
        """ Return representation for an Input, including dependents inputs if needed """
        if obj.dependents_inputs.count() > 0:
            return ConditionalInputSerializer(obj, context=self.context).to_representation(obj)
        else:
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
                return AParamSerializer(obj, context=self.context).to_representation(obj)


class RelatedInputSerializer(InputSerializer):
    """ Serialize a dependent Input (RelatedParam models) """

    class Meta:
        model = RelatedParam
        fields = InputSerializer.Meta.fields

    def to_representation(self, instance):
        """ Return representation of a Related Input """
        initial_repr = super(RelatedInputSerializer, self).to_representation(instance)
        return {instance.when_value: initial_repr}


class ConditionalInputSerializer(DynamicFieldsModelSerializer):
    """ Serialize inputs if it's a conditional one """

    class Meta:
        model = AParam
        fields = ('label', 'name', 'default', 'type', 'cmd_format', 'mandatory', 'description', 'multiple', 'when')

    when = RelatedInputSerializer(source='dependents_inputs', many=True, read_only=True)
    description = serializers.CharField(source='help_text')