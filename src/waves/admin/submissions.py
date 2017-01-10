""" Service Submission administration classes """
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.admin import StackedInline, TabularInline
from django.urls import reverse
from django.utils.safestring import mark_safe
import nested_admin
from waves.compat import WavesModelAdmin, CompactInline
# from waves.forms.admin.submissions import *
from waves.models.submissions import *
from waves.models.inputs import *
from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin, PolymorphicSortableAdminMixin
from polymorphic.admin import PolymorphicInlineSupportMixin, StackedPolymorphicInline


class ServiceOutputInline(SortableInlineAdminMixin, CompactInline, admin.TabularInline):
    """ Service Submission Outputs Inlines """
    model = SubmissionOutput
    # form = ServiceOutputForm
    sortable = 'order'
    show_change_link = False
    extra = 0
    classes = ('collapse',)
    sortable_field_name = "order"
    sortable_options = []
    fk_name = 'submission'
    fields = ['name', 'file_pattern', 'optional', 'from_input', 'order']
    verbose_name_plural = "Outputs"


class ServiceSampleDependentInputInline(admin.TabularInline):
    model = SampleDepParam
    fk_name = 'sample'
    extra = 0


class ServiceExitCodeInline(admin.TabularInline):
    model = SubmissionExitCode
    extra = 0
    fk_name = 'submission'
    is_nested = False
    classes = ('collapse', 'grp-collapse', 'grp-open')
    sortable_options = []


class OrganizeInputInline(SortableInlineAdminMixin, admin.TabularInline):
    model = InputParam
    fields = ['name', 'default', 'class_label', 'related_to', 'order']
    readonly_fields = ['class_label', 'related_to']
    verbose_name_plural = "Organize Inputs"
    verbose_name = "Organize Inputs"
    can_delete = False
    extra = 0
    show_change_link = True

    def class_label(self, obj):
        return obj.class_label
    class_label.short_description = "Input type"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        return InputParam.objects.all()


class PolymorphicInputInlineChild(StackedPolymorphicInline.Child):

    classes = ['collapse', ]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'repeat_group':
            kwargs['queryset'] = RepeatedGroup.objects.filter(submission=request.current_obj)
        return super(PolymorphicInputInlineChild, self).formfield_for_foreignkey(db_field, request, **kwargs)


class SubmitInputsInline(StackedPolymorphicInline, CompactInline):
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

    class TextParamInline(PolymorphicInputInlineChild):
        model = TextParam
        exclude = ['order']

    model = InputParam
    exclude = ['order']
    verbose_name = "Param"
    verbose_name_plural = "Params"
    classes = ['collapse', ]
    child_inlines = (
        TextParamInline,
        BooleanParamInline,
        ListParamInline,
        IntegerParamInline,
        DecimalParamInline,
    )
    list_display_links = None
    list_display = ('name', '__class__', 'default')


class FileInputInline(CompactInline, SortableInlineAdminMixin):
    model = FileInput
    extra = 0

# import nested_admin
class FileInputSampleInline(SortableInlineAdminMixin, TabularInline):
    model = FileInputSample
    extra = 0
    fk_name = 'submission'
    verbose_name = "File Sample"
    verbose_name_plural = "Files samples"


class RepeatGroupAdmin(WavesModelAdmin):
    # readonly_fields = ['submission']
    # readonly_fields = ['submission']
    exclude = ['submission', ]

    def has_module_permission(self, request):
        return False


class OrgRepeatGroupInline(CompactInline):
    model = RepeatedGroup
    extra = 0
    verbose_name = "Input group"
    verbose_name_plural = "Organize Groups"


class ServiceSubmissionAdmin(PolymorphicInlineSupportMixin, admin.ModelAdmin):
    """ Submission process administration -- Model Submission """

    class Media:
        js = ('waves/admin/js/services.js',)

    inlines = [
        SubmitInputsInline,
        FileInputInline,
        ServiceOutputInline,
        ServiceExitCodeInline,
        OrganizeInputInline,
        OrgRepeatGroupInline
    ]
    # fields = ('label', 'api_name', 'service', 'available_api', 'available_online')
    exclude = ['order']
    change_form_template = 'admin/waves/submission/change_form.html'
    list_display = ['label', 'available_online', 'available_api', 'service_link', ]
    readonly_fields = ['available_online', 'available_api']
    list_filter = ['service', 'availability']
    fieldsets = [
        ('General', {
            'fields': ('label', 'api_name', 'availability', 'service', 'available_api', 'available_online'),
            'classes': ['collapse']
        }),
    ]
    tabs = [
        ('FileInputs', (
            SubmitInputsInline,
        )),
        ('Outputs', (
            ServiceOutputInline,
            ServiceExitCodeInline
        ))
    ]

    def get_form(self, request, obj=None, **kwargs):
        request.current_obj = obj
        return super(ServiceSubmissionAdmin, self).get_form(request, obj, **kwargs)

    def has_module_permission(self, request):
        return False

    def service_link(self, obj):
        """ Back link to related service """
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse("admin:waves_service_change", args=(obj.service.id,)),
            obj.service.name))

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


admin.site.register(Submission, ServiceSubmissionAdmin)
admin.site.register(RepeatedGroup, RepeatGroupAdmin)
