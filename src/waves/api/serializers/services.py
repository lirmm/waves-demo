from __future__ import unicode_literals

import logging
from rest_framework import serializers
from rest_framework.fields import empty
from django.utils.html import strip_tags
from rest_framework.reverse import reverse as reverse_drf
from dynamic import DynamicFieldsModelSerializer
from waves.models import ServiceInput, ServiceOutput, ServiceMeta, Service, RelatedInput, Job, ServiceSubmission
from waves.api.serializers.base import WavesModelSerializer
import waves.settings

__all__ = ['InputSerializer', 'InputSerializer', 'MetaSerializer', 'OutputSerializer', 'ServiceSerializer',
           'ServiceFormSerializer', 'ServiceSubmissionSerializer', 'ServiceMetaSerializer']
logger = logging.getLogger(__name__)


class InputSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = ServiceInput
        fields = ('label', 'name', 'default', 'type', 'format', 'mandatory', 'short_description',
                  'multiple')
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
        fields = (
            'label', 'name', 'default', 'type', 'format', 'mandatory', 'short_description', 'description', 'multiple',
            'when')

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

    def to_representation(self, instance):
        to_repr = {}
        for meta in instance.all():
            to_repr[meta.type] = {
                "type": meta.get_type_display(),
                "title": meta.title,
                "description": meta.short_description if meta.short_description is not None else strip_tags(
                    meta.description),
                "text": meta.value
            }
        return to_repr


class ServiceMetaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Service
        fields = ('url', 'name', 'metas_info')
        extra_kwargs = {
            'url': {'view_name': 'waves:waves-services-detail', 'lookup_field': 'api_name'}
        }

    metas_info = MetaSerializer(read_only=True, source="all_metas")


class ServiceSubmissionSerializer(DynamicFieldsModelSerializer, serializers.HyperlinkedRelatedField):
    class Meta:
        model = ServiceSubmission
        fields = ('label', 'default', 'service', 'submission_uri', 'form', 'inputs')
        extra_kwargs = {
            'api_name': {'view_name': 'waves:waves-submission-detail', 'lookup_fields': {'api_name', 'api_name'}},
        }

    view_name = 'waves:waves-services-submissions'
    submission_uri = serializers.SerializerMethodField()
    inputs = InputSerializer(many=True, read_only=True, source="submitted_service_inputs")
    form = serializers.SerializerMethodField()
    service = serializers.SerializerMethodField()

    def get_form(self, obj):
        return reverse_drf(viewname='waves:waves-services-submissions-form', request=self.context['request'],
                           kwargs={'service': obj.service.api_name,
                                   'api_name': obj.api_name})

    def get_submission_uri(self, obj):
        return reverse_drf(viewname='waves:waves-services-submissions', request=self.context['request'],
                           kwargs={'service': obj.service.api_name,
                                   'api_name': obj.api_name})

    def get_service(self, obj):
        return reverse_drf(viewname='waves:waves-services-detail', request=self.context['request'],
                           kwargs={'api_name': obj.service.api_name})

    def get_queryset(self):
        return ServiceSubmission.objects.filter(available_api=True)


class ServiceSerializer(serializers.HyperlinkedModelSerializer, DynamicFieldsModelSerializer):
    class Meta:
        model = Service
        fields = ('url', 'category', 'name', 'version', 'created', 'short_description',
                  'default_submission_uri', 'jobs', 'metas', 'submissions')
        lookup_field = 'api_name'
        extra_kwargs = {
            'url': {'view_name': 'waves:waves-services-detail', 'lookup_field': 'api_name'},
        }

    category = serializers.HyperlinkedRelatedField(many=False,
                                                   read_only=True,
                                                   view_name='waves:waves-services-category-detail',
                                                   lookup_field='api_name')
    jobs = serializers.SerializerMethodField()
    metas = serializers.SerializerMethodField()
    submissions = ServiceSubmissionSerializer(many=True, read_only=True, hidden=('service',))
    default_submission_uri = serializers.SerializerMethodField()

    def get_default_submission_uri(self, obj):
        if obj.default_submission is not None:
            return reverse_drf(viewname='waves:waves-services-submissions', request=self.context['request'],
                               kwargs={'service': obj.api_name,
                                       'api_name': obj.default_submission.api_name})
        else:
            logger.warning('Service %s has no default submission', obj)


    def get_jobs(self, obj):
        return reverse_drf(viewname='waves:waves-services-jobs', request=self.context['request'],
                           kwargs={'api_name': obj.api_name})

    def get_metas(self, obj):
        return reverse_drf(viewname='waves:waves-services-metas', request=self.context['request'],
                           kwargs={'api_name': obj.api_name})


class ServiceFormSerializer(WavesModelSerializer):
    class Meta:
        model = ServiceSubmission
        fields = ('label', 'service', 'js', 'css', 'template_pack', 'post_uri', 'form')

    js = serializers.SerializerMethodField(source='url_js')
    css = serializers.SerializerMethodField()
    form = serializers.SerializerMethodField()
    post_uri = serializers.SerializerMethodField()
    template_pack = serializers.SerializerMethodField()
    service = serializers.SerializerMethodField()

    def get_template_pack(self, obj):
        return waves.settings.WAVES_TEMPLATE_PACK

    def get_css(self, obj):
        return self.get_fully_qualified_url(obj.service.url_js)

    def get_js(self, obj):
        return self.get_fully_qualified_url(obj.service.url_css)

    def get_form(self, obj):
        from waves.forms.services import ServiceForm
        from django.template import RequestContext
        import re
        form = ServiceForm(instance=self.instance.service, submission=self.instance.api_name)
        return re.sub(r'\s\s+', '', form.helper.render_layout(form, context=RequestContext(self.context['request'])))

    def get_post_uri(self, obj):
        return reverse_drf(viewname='waves:waves-services-submissions', request=self.context['request'],
                           kwargs={'api_name': obj.api_name, 'service': obj.service.api_name})

    def get_service(self, obj):
        return reverse_drf(viewname='waves:waves-services-detail', request=self.context['request'],
                           kwargs={'api_name': obj.service.api_name})
