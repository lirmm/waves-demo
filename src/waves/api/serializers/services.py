from __future__ import unicode_literals

from rest_framework import serializers
from rest_framework.fields import empty
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site

from dynamic import DynamicFieldsModelSerializer
from waves.models import ServiceInput, ServiceOutput, ServiceMeta, Service, RelatedInput, Job
from waves.managers.servicejobs import ServiceJobManager
from waves.api.serializers.base import WavesModelSerializer
import waves.settings


class InputSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = ServiceInput
        fields = ('label', 'name', 'default', 'type', 'format', 'mandatory', 'description', 'multiple')
        extra_kwargs = {
            'url': {'view_name': 'waves:waves-services-detail', 'lookup_field': 'api_name'}
        }

    format = serializers.SerializerMethodField()

    def get_format(self, obj):
        return ', '.join(obj.format.splitlines())

    def __init__(self, instance=None, data=empty, **kwargs):
        super(InputSerializer, self).__init__(instance, data, **kwargs)

    def to_representation(self, instance):
        if hasattr(instance, 'dependent_inputs') and instance.dependent_inputs.count() > 0:
            representation = ConditionalInputSerializer(instance, context=self.context).to_representation(instance)
        else:
            representation = super(InputSerializer, self).to_representation(instance)
        return representation


class RelatedInputSerializer(InputSerializer):
    class Meta:
        model = RelatedInput
        fields = InputSerializer.Meta.fields
        # fields = ('label', 'name', 'default', 'type', 'format', 'description', 'multiple')

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

    format = serializers.SerializerMethodField()

    def get_format(self, obj):
        return ', '.join(obj.format.splitlines())


class OutputSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = ServiceOutput
        exclude = ('order', 'id', 'service', 'from_input')


class MetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceMeta
        fields = ('title', 'value', 'short_description', 'description')


class ServiceSerializer(serializers.HyperlinkedModelSerializer, DynamicFieldsModelSerializer):
    class Meta:
        model = Service
        fields = ('url', 'category', 'name', 'version', 'created', 'short_description',
                  'form', 'jobs', 'inputs', 'metas')
        lookup_field = 'api_name'
        extra_kwargs = {
            'url': {'view_name': 'waves:waves-services-detail', 'lookup_field': 'api_name'},
        }

    metas = MetaSerializer(many=True,
                           read_only=True)
    inputs = InputSerializer(many=True,
                             read_only=True,
                             source='base_inputs')
    category = serializers.HyperlinkedRelatedField(many=False,
                                                   read_only=True,
                                                   view_name='waves:waves-services-category-detail',
                                                   lookup_field='name')
    jobs = serializers.SerializerMethodField()
    form = serializers.SerializerMethodField()

    def get_jobs(self, obj):
        return 'http://%s%s' % (
            Site.objects.get_current().domain, reverse('waves:waves-services-jobs', kwargs={'api_name': obj.api_name}))

    def get_form(self, obj):
        return 'http://%s%s' % (
            Site.objects.get_current().domain, reverse('waves:waves-services-form', kwargs={'api_name': obj.api_name}))


class ServiceJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ('client', 'service')

    def validate(self, attrs):
        print 'validate call', attrs
        return super(ServiceJobSerializer, self).validate(attrs)

    def run_validation(self, data=empty):
        print "run validation", data
        return super(ServiceJobSerializer, self).run_validation(data)

    def is_valid(self, raise_exception=False):
        print 'validation data ', self.initial_data
        return super(ServiceJobSerializer, self).is_valid(raise_exception)

    def create(self, validated_data):
        client = validated_data.pop('client')
        try:
            ass_email = validated_data['email']
        except KeyError:
            ass_email = None
            pass
        self.instance = ServiceJobManager.create_new_job(service=validated_data['service'],
                                                         email_to=ass_email,
                                                         submitted_inputs=self.initial_data,
                                                         user=client)
        return self.instance


class ServiceFormSerializer(WavesModelSerializer):
    class Meta:
        model = Service
        fields = ('api_name', 'name', 'short_description', 'js', 'css', 'template_pack', 'post_uri', 'form')
    js = serializers.SerializerMethodField(source='url_js')
    css = serializers.SerializerMethodField()
    form = serializers.SerializerMethodField()
    post_uri = serializers.SerializerMethodField()
    template_pack = serializers.SerializerMethodField()

    def get_template_pack(self, obj):
        return waves.settings.WAVES_TEMPLATE_PACK

    def get_css(self, obj):
        return self.get_fully_qualified_url(obj.url_js)

    def get_js(self, obj):
        return self.get_fully_qualified_url(obj.url_css)

    def get_form(self, obj):
        from waves.forms.services import ServiceJobForm
        from django.template import RequestContext
        import re
        form = ServiceJobForm(instance=self.instance)
        return re.sub(r'\s\s+', '', form.helper.render_layout(form, context=RequestContext(self.context['request'])))

    def get_post_uri(self, obj):
        return self.get_fully_qualified_url(reverse('waves:waves-services-jobs', kwargs={'api_name': obj.api_name}))
