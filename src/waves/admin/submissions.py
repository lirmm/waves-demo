""" Service Submission administration classes """
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.admin import StackedInline
from django.urls import reverse
from django.utils.safestring import mark_safe
from jet.admin import CompactInline
import nested_admin
import waves.const
from waves.admin.base import WavesTabbedModelAdmin
# from waves.forms.admin import ServiceOutputForm, ParamForm
from waves.forms.admin.submissions import *
from waves.models import SubmissionExitCode
from waves.models.submissions import *


class ServiceOutputInline(CompactInline):
    model = SubmissionOutput
    # form = ServiceOutputForm
    sortable = 'order'
    extra = 0
    classes = ('collapse',)
    sortable_field_name = "order"
    sortable_options = []
    fk_name = 'submission'
    fields = ['name', 'file_pattern', 'short_description', 'optional', 'from_input', 'order']
    verbose_name_plural = "Outputs"
    show_change_link = True


class ServiceSampleDependentInputInline(admin.TabularInline):
    model = SampleDependentParam
    fk_name = 'sample'
    extra = 0
    sortable_field_name = "order"
    sortable_options = []

"""
class ServiceSampleInline(CompactInline, nested_admin.NestedStackedInline):
    model = SubmissionSample
    form = ServiceInputSampleForm
    extra = 0
    fk_name = 'service'
    is_nested = False
    verbose_name_plural = "Service sample ('input' apply only to 'default' submission params)"
    inlines = [
        ServiceSampleDependentInputInline
    ]

    def get_field_queryset(self, db, db_field, request):
        field_queryset = super(ServiceSampleInline, self).get_field_queryset(db, db_field, request)
        if request.current_obj is not None:
            if db_field.name == 'input':
                return SubmissionParam.objects.filter(service=request.current_obj.default_submission,
                                                      type=waves.const.TYPE_FILE)
            elif db_field.name == 'dependent_input':
                return SubmissionParam.objects.filter(service=request.current_obj.default_submission).exclude(
                    type=waves.const.TYPE_FILE)
        return field_queryset

"""

class RelatedInputInline(nested_admin.NestedStackedInline, StackedInline):
    model = RelatedParam
    # form = RelatedInputForm
    extra = 0
    sortable = 'order'
    fk_name = 'related_to'
    # readonly_fields = ['baseinput_ptr']
    sortable_excludes = ('order',)
    verbose_name = 'Related Input'
    verbose_name_plural = "Related Inputs"

    def has_add_permission(self, request):
        return True


class SubmissionDataInline(CompactInline):
    model = SubmissionData
    fk_name = 'submission'
    extra = 0
    exclude = ['id', 'order', 'description']
    fields = ['label', 'name', 'cmd_line_type', 'list_elements', 'required', 'multiple',
              'submitted', 'short_description', 'edam_formats', 'edam_datas']


class SubmissionParamInline(SubmissionDataInline):
    model = SubmissionParam
    form = ParamForm
    verbose_name = 'Param'
    verbose_name_plural = "Params"
    fields = ['type', 'default', ] + SubmissionDataInline.fields

    def get_queryset(self, request):
        qs = super(SubmissionParamInline, self).get_queryset(request)
        return qs  # .instance_of(SubmissionParam)


class RelatedParamInline(SubmissionParamInline):
    model = RelatedParam
    fields = ['related_to', 'when_value'] + SubmissionParamInline.fields
    verbose_name = 'Related param'
    verbose_name_plural = "Related params"


class SubmissionFileInputInline(SubmissionDataInline):
    model = FileInput
    form = FileInputForm
    verbose_name = 'Input'
    verbose_name_plural = "Inputs"
    exclude = SubmissionDataInline.exclude + ['when_value', 'related_to', 'type', 'list_display', 'default']


class RelatedFileInputInline(SubmissionParamInline):
    model = RelatedFileInput
    verbose_name = 'Related input'
    verbose_name_plural = "Related inputs"
    fields = ('related_to', 'label', 'name', 'cmd_line_type', 'list_elements', 'required', 'multiple',
              'short_description', 'edam_formats', 'edam_datas')
    exclude = ('type', 'list_display', 'default')


class ServiceExitCodeInline(CompactInline):
    model = SubmissionExitCode
    extra = 0
    fk_name = 'submission'
    is_nested = False
    classes = ('grp-collapse', 'grp-open')
    sortable_options = []


class ServiceSubmissionAdmin(admin.ModelAdmin):
    """ Submission process administration -- Model ServiceSubmission """
    class Media:
        js = ('waves/admin/js/services.js',)

    inlines = [
        SubmissionFileInputInline,
        RelatedFileInputInline,
        SubmissionParamInline,
        RelatedParamInline,
        ServiceOutputInline,
        ServiceExitCodeInline
    ]
    fields = ('label', 'api_name', 'service', 'available_api', 'available_online')
    exclude = ['order']
    change_form_template = 'admin/waves/submission/change_form.html'
    list_display = ['label', 'available_online', 'available_api', 'service_link', ]
    list_filter = ['service', 'available_online', 'available_api']

    def service_link(self, obj):
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse("admin:waves_service_change", args=(obj.service.id,)),
            obj.service.name))

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super(ServiceSubmissionAdmin, self).get_readonly_fields(request, obj))
        if obj is not None:
            readonly_fields.append('service')
        return readonly_fields


admin.site.register(ServiceSubmission, ServiceSubmissionAdmin)

