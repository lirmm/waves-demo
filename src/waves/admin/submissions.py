""" Service Submission administration classes """
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.admin import StackedInline, TabularInline
from django.urls import reverse
from django.utils.safestring import mark_safe
import nested_admin
from waves.apps import WavesModelAdmin, WavesCompactInline as CompactInline
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


class ServiceSampleInline(CompactInline):
    model = FileInputSample
    # form = ServiceInputSampleForm
    extra = 0
    fk_name = 'file_input__submission'
    is_nested = False
    verbose_name = "Input Sample"
    verbose_name_plural = "Input files samples"

    """
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


class RelatedInputInline(SortableInlineAdminMixin, StackedInline):
    model = BaseParam
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


class SubmissionDataInlineMixin(object):
    fields = ['label', 'name', 'cmd_format', 'required', 'help_text', 'edam_formats',
              'edam_datas', 'multiple', ]
    fk_name = 'submission'
    extra = 0
    classes = ['collapse']
    exclude = ['id']


class RelatedParamInline(PolymorphicSortableAdminMixin, StackedPolymorphicInline):
    class BooleanParamInline(StackedPolymorphicInline.Child):
        model = BooleanRelatedParam
        exclude = ['order']

    class FileInputInline(StackedPolymorphicInline.Child):
        model = FileRelatedParam
        exclude = ['order']

    class ListParamInline(StackedPolymorphicInline.Child):
        model = ListRelatedParam
        exclude = ['order']

    class NumberParamInline(StackedPolymorphicInline.Child):
        model = NumberRelatedParam
        exclude = ['order']

    class TextParamInline(StackedPolymorphicInline.Child):
        model = TextRelatedParam
        exclude = ['order']
    model = BaseParam
    fields = ['related_to', 'when_value'] + SubmissionDataInlineMixin.fields
    verbose_name = 'Dependent param'
    verbose_name_plural = "Dependent params"
    list_display_links = None
    list_display = ('related_to', 'when_value', 'default')


class ServiceExitCodeInline(CompactInline):
    model = SubmissionExitCode
    extra = 0
    fk_name = 'submission'
    is_nested = False
    classes = ('collapse', 'grp-collapse', 'grp-open')
    sortable_options = []


class OrganizeInputInline(SortableInlineAdminMixin, admin.TabularInline):
    model = BaseParam
    fields = ['name', 'default', 'clazz_name', 'order']
    readonly_fields = ['clazz_name', ]
    verbose_name_plural = "Organize Inputs"
    verbose_name = "Organize Inputs"
    can_delete = False
    extra = 0
    show_change_link = True

    def clazz_name(self, obj):
        return obj.__class__.__name__

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        return BaseParam.objects.not_instance_of(RelatedParam)


class SubmitInputsInline(StackedPolymorphicInline):

    class BooleanParamInline(StackedPolymorphicInline.Child):
        model = BooleanParam
        exclude = ['order']

    class FileInputInline(StackedPolymorphicInline.Child):
        model = FileInput
        exclude = ['order']

    class ListParamInline(StackedPolymorphicInline.Child):
        model = ListParam
        exclude = ['order']

    class NumberParamInline(StackedPolymorphicInline.Child):
        model = NumberParam
        exclude = ['order']

    class TextParamInline(StackedPolymorphicInline.Child):
        model = TextParam
        exclude = ['order']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'repeat_group':
            print "Yeahhhh"
        return super(SubmitInputsInline, self).formfield_for_foreignkey(db_field, request, **kwargs)

    model = BaseParam
    exclude = ['order']
    verbose_name = "Param"
    verbose_name_plural = "Params"
    child_inlines = (
        BooleanParamInline,
        FileInputInline,
        ListParamInline,
        NumberParamInline,
        TextParamInline
    )
    list_display_links = None
    list_display = ('name', 'default')


# import nested_admin
class FileInputSampleInline(SortableInlineAdminMixin, TabularInline):
    model = FileInputSample
    extra = 0
    fk_name = 'submission'
    verbose_name = "Input Sample"
    verbose_name_plural = "Input files samples"

class RepeatGroupAdmin(WavesModelAdmin):
    # readonly_fields = ['submission']
    # readonly_fields = ['submission']

    def has_module_permission(self, request):
        return False


class RepeatGroupInline(CompactInline):
    model = RepeatedGroup
    extra = 0
    verbose_name = "Repeat group"
    verbose_name_plural = "Manage Repeat Group"

class ServiceSubmissionAdmin(PolymorphicInlineSupportMixin, WavesModelAdmin):
    """ Submission process administration -- Model Submission """

    class Media:
        js = ('waves/admin/js/services.js',)

    inlines = [
        SubmitInputsInline,
        FileInputSampleInline,
        ServiceOutputInline,
        ServiceExitCodeInline,
        OrganizeInputInline,
        RepeatGroupInline
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

    def service_link(self, obj):
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse("admin:waves_service_change", args=(obj.service.id,)),
            obj.service.name))

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
