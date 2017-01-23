""" Service Submission administration classes """
from __future__ import unicode_literals

from adminsortable2.admin import SortableInlineAdminMixin
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.urls import reverse
from django.utils.safestring import mark_safe
from polymorphic.admin import PolymorphicInlineSupportMixin, StackedPolymorphicInline

from waves.admin.base import WavesModelAdmin
from waves.admin.forms.services import SampleDepForm, InputInlineForm, TextParamForm, InputSampleForm
from waves.compat import CompactInline
from waves.models.inputs import *
from waves.models.submissions import *


class SubmissionRunnerParamInLine(GenericTabularInline):
    model = SubmissionRunParam
    # form = ServiceRunnerParamForm
    fields = ['name', 'value']
    extra = 0
    classes = ('grp-collapse grp-closed', 'collapse')
    suit_classes = 'suit-tab suit-tab-adaptor'
    can_delete = False
    readonly_fields = ['name']
    is_nested = False
    sortable_options = []
    verbose_name_plural = "Run configuration"
    verbose_name = "Run configuration"

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def get_queryset(self, request):
        return super(SubmissionRunnerParamInLine, self).get_queryset(request).filter(prevent_override=False)


class ServiceOutputInline(CompactInline):
    """ Service Submission Outputs Inlines """
    model = SubmissionOutput
    # form = ServiceOutputForm
    show_change_link = False
    extra = 0
    sortable_field_name = "order"
    sortable_options = []
    fk_name = 'submission'
    fields = ['label', 'ext', 'name', 'optional', 'from_input', 'file_pattern', 'edam_format', 'edam_data']
    verbose_name_plural = "Outputs"
    classes = ('grp-collapse', 'grp-closed', 'collapse')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "from_input":
            kwargs['queryset'] = BaseParam.objects.filter(submission=request.current_obj)
        return super(ServiceOutputInline, self).formfield_for_foreignkey(db_field, request, **kwargs)


class SampleDependentInputInline(CompactInline):
    model = SampleDepParam
    form = SampleDepForm
    fk_name = 'submission'
    extra = 0
    classes = ('grp-collapse grp-closed', 'collapse')

    def has_add_permission(self, request):
        if request.current_obj is not None and request.current_obj.submission_samples.count() > 0:
            return True
        return False

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "related_to":
            kwargs['queryset'] = BaseParam.objects.filter(submission=request.current_obj).not_instance_of(FileInput)
        return super(SampleDependentInputInline, self).formfield_for_foreignkey(db_field, request, **kwargs)


class ExitCodeInline(admin.TabularInline):
    model = SubmissionExitCode
    extra = 0
    fk_name = 'submission'
    is_nested = False
    classes = ('grp-collapse grp-closed', 'collapse')
    sortable_options = []


class OrganizeInputInline(SortableInlineAdminMixin, admin.TabularInline):
    model = BaseParam
    form = InputInlineForm
    fields = ['class_label', 'label', 'name', 'required', 'default', 'order']
    readonly_fields = ['class_label']
    classes = ('grp-collapse', 'grp-closed', 'collapse', 'show-change-link-popup')
    can_delete = True
    extra = 0
    show_change_link = True

    def class_label(self, obj):

        # if obj.related_to:
        #    return "-- %s (%s)" % (obj.class_label, obj.related_to.label)
        return obj.class_label

    class_label.short_description = "Input type"

    def has_add_permission(self, request):
        return False

    def get_queryset(self, request):
        # TODO order fields according to related also (display first level items just followed by their dependents)
        return BaseParam.objects.all()


class PolymorphicInputInlineChild(StackedPolymorphicInline.Child):
    classes = ['collapse', ]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'repeat_group':
            kwargs['queryset'] = RepeatedGroup.objects.filter(submission=request.current_obj)
        return super(PolymorphicInputInlineChild, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def get_fields(self, request, obj=None):
        # TODO only use required fields
        return super(PolymorphicInputInlineChild, self).get_fields(request, obj)


class SubmitInputsInline(StackedPolymorphicInline):
    class BooleanParamInline(PolymorphicInputInlineChild):
        model = BooleanParam
        exclude = ['order']
        classes = ['collapse']

    class ListParamInline(PolymorphicInputInlineChild):
        model = ListParam
        exclude = ['order']

    class DecimalParamInline(PolymorphicInputInlineChild):
        model = DecimalParam
        exclude = ['order']

    class IntegerParamInline(PolymorphicInputInlineChild):
        model = IntegerParam
        exclude = ['order']

    class BaseParamInline(PolymorphicInputInlineChild):
        model = BaseParam

    class TextParamInline(PolymorphicInputInlineChild):
        model = BaseParam
        exclude = ['order']
        form = TextParamForm

    class FileInputInline(PolymorphicInputInlineChild):
        model = FileInput
        exclude = ['order']

    model = BaseParam
    exclude = ['order']
    verbose_name = "Param"
    verbose_name_plural = "Params"
    classes = ['collapse', ]
    show_change_link = True
    show_full_result_count = True
    child_inlines = (
        TextParamInline,
        FileInputInline,
        BooleanParamInline,
        ListParamInline,
        IntegerParamInline,
        DecimalParamInline,
    )
    list_display_links = None
    list_display = ('name', '__class__', 'default')

    def get_fields(self, request, obj=None):
        # TODO only use required fields
        return super(SubmitInputsInline, self).get_fields(request, obj)

    def __init__(self, parent_model, admin_site):
        super(SubmitInputsInline, self).__init__(parent_model, admin_site)


class FileInputSampleInline(CompactInline):
    model = FileInputSample
    form = InputSampleForm
    extra = 0
    fk_name = 'submission'
    fields = ['label', 'file', 'file_input']
    exclude = ['order']
    classes = ('grp-collapse grp-closed', 'collapse')

    def has_add_permission(self, request):
        if request.current_obj is not None and request.current_obj.submission_inputs.instance_of(FileInput).count() > 0:
            return True
        return False


@admin.register(RepeatedGroup)
class RepeatGroupAdmin(WavesModelAdmin):
    # readonly_fields = ['submission']
    # readonly_fields = ['submission']
    exclude = ['order']

    def get_model_perms(self, request):
        return {}  # super(AllParamModelAdmin, self).get_model_perms(request)


class OrgRepeatGroupInline(CompactInline):
    model = RepeatedGroup
    extra = 0
    verbose_name = "Input group"
    exclude = ['order']
    verbose_name_plural = "Input groups"
    classes = ('grp-collapse grp-closed', 'collapse')


@admin.register(Submission)
class ServiceSubmissionAdmin(PolymorphicInlineSupportMixin, WavesModelAdmin):
    """ Submission process administration -- Model Submission """

    class Media:
        js = ('waves/admin/js/services.js',)

    inlines = [
        SubmissionRunnerParamInLine,
        OrganizeInputInline,
        # OrgRepeatGroupInline,
        ServiceOutputInline,
        FileInputSampleInline,
        SampleDependentInputInline,
        ExitCodeInline,
    ]

    def get_model_perms(self, request):
        return {}  # super(AllParamModelAdmin, self).get_model_perms(request)

    # fields = ('label', 'api_name', 'service', 'available_api', 'available_online')
    exclude = ['order']
    save_on_top = True
    change_form_template = 'admin/waves/submission/change_form.html'
    list_display = ['label', 'available_online', 'available_api', 'service_link', 'runner']
    readonly_fields = ['available_online', 'available_api']
    list_filter = (
        'service__name',
        'availability'
    )
    search_fields = ('service__name', 'label', 'override_runner__name', 'service__runner__name')
    fieldsets = [
        ('General', {
            'fields': ['label', 'api_name', 'availability', 'service', 'override_runner', 'available_api',
                       'available_online'],
            'classes': ['collapse']
        }),
    ]
    show_full_result_count = True
    tabs = [
        ('FileInputs', (
            SubmitInputsInline,
        )),
        ('Outputs', (
            ServiceOutputInline,
            ExitCodeInline
        ))
    ]

    def add_view(self, request, form_url='', extra_context=None):
        context = extra_context or {}
        context['show_save_as_new'] = False
        context['show_save_and_add_another'] = False
        context['show_save'] = False
        return super(ServiceSubmissionAdmin, self).add_view(request, form_url, context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        return super(ServiceSubmissionAdmin, self).change_view(request, object_id, form_url, extra_context)

    def get_form(self, request, obj=None, **kwargs):
        request.current_obj = obj
        form = super(ServiceSubmissionAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['override_runner'].widget.can_add_related = False
        form.base_fields['override_runner'].widget.can_change_related = False
        form.base_fields['override_runner'].widget.can_delete_related = False
        return form

    def get_fieldsets(self, request, obj=None):
        fieldsets = super(ServiceSubmissionAdmin, self).get_fieldsets(request, obj)
        if obj is None:  # i.e create mode
            elem = fieldsets[0][1]
            elem['classes'].append('open') if 'open' not in elem['classes'] else None
            elem['fields'].remove('available_api') if 'available_api' in elem['fields'] else None
            elem['fields'].remove('available_online') if 'available_online' in elem['fields'] else None
            elem['fields'].remove('api_name') if 'api_name' in elem['fields'] else None
        return fieldsets

    def service_link(self, obj):
        """ Back link to related service """
        return mark_safe('<a class="button btn" href="{}">Edit Service</a>'.format(
            reverse("admin:waves_service_change", args=(obj.service.id,))))

    service_link.short_description = "Related Service"

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super(ServiceSubmissionAdmin, self).get_readonly_fields(request, obj))
        if obj is not None:
            readonly_fields.append('service')
        return readonly_fields

    def available_api(self, obj):
        return obj.available_api

    def available_online(self, obj):
        return obj.available_online
