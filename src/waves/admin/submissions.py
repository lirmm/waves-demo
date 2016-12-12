""" Service Submission administration classes """
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.admin import StackedInline
from django.urls import reverse
from django.utils.safestring import mark_safe
from jet.admin import CompactInline
from nested_inline import admin as nested_admin

import waves.const
from waves.admin.base import WavesTabbedModelAdmin
from waves.forms.admin import ServiceOutputForm, ServiceInputSampleForm, ServiceInputForm
from waves.forms.admin.submissions import RelatedInputForm
from waves.models.submissions import *


class ServiceOutputInline(CompactInline):
    model = ServiceOutput
    form = ServiceOutputForm
    sortable = 'order'
    extra = 0
    classes = ('collapse',)
    sortable_field_name = "order"
    sortable_options = []
    fk_name = 'service'
    fields = ['name', 'file_pattern', 'short_description', 'may_be_empty', 'related_from_input', 'order']
    verbose_name_plural = "Service outputs"
    show_change_link = True


class ServiceSampleDependentInputInline(admin.TabularInline):
    model = ServiceSampleDependentInput
    fk_name = 'sample'
    extra = 0
    sortable_field_name = "order"
    sortable_options = []


class ServiceSampleInline(CompactInline, nested_admin.NestedStackedInline):
    model = ServiceInputSample
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
                return ServiceInput.objects.filter(service=request.current_obj.default_submission,
                                                   type=waves.const.TYPE_FILE)
            elif db_field.name == 'dependent_input':
                return ServiceInput.objects.filter(service=request.current_obj.default_submission).exclude(
                    type=waves.const.TYPE_FILE)
        return field_queryset


class RelatedInputInline(nested_admin.NestedStackedInline, StackedInline):
    model = RelatedInput
    form = RelatedInputForm
    extra = 0
    sortable = 'order'
    fk_name = 'related_to'
    # readonly_fields = ['baseinput_ptr']
    sortable_excludes = ('order',)
    verbose_name = 'Related Input'
    verbose_name_plural = "Related Inputs"

    def has_add_permission(self, request):
        return True


class ServiceInputInline(CompactInline, nested_admin.NestedStackedInline):
    model = ServiceInput
    form = ServiceInputForm
    sortable = 'order'
    extra = 0
    fk_name = 'service'
    classes = ('collapse', 'closed')
    inlines = [RelatedInputInline, ]
    sortable_field_name = "order"
    verbose_name = 'Input'
    verbose_name_plural = "Inputs"
    show_change_link = True

    def get_queryset(self, request):
        qs = super(ServiceInputInline, self).get_queryset(request)
        return qs  # .instance_of(ServiceInput)


class ServiceSubmissionAdmin(WavesTabbedModelAdmin):
    """ Submission process administration -- Model ServiceSubmission """
    inlines = [ServiceInputInline]
    list_display = ['label',
                    'available_online',
                    'available_api',
                    'service_link', ]

    list_filter = ['service', 'available_online', 'available_api']

    def service_link(self, obj):
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse("admin:waves_service_change", args=(obj.service.id,)),
            obj.service.name))

admin.site.register(ServiceSubmission, ServiceSubmissionAdmin)
