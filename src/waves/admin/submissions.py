""" Service Submission administration classes """
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.admin import StackedInline, TabularInline
from django.urls import reverse
from django.utils.safestring import mark_safe
# import nested_admin
from waves.admin.base import WavesModelAdmin
from waves.compat import CompactInline
from waves.models.submissions import *
from waves.models.inputs import *
from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin, PolymorphicSortableAdminMixin

from polymorphic.admin import PolymorphicInlineSupportMixin, StackedPolymorphicInline, PolymorphicInlineModelAdmin


class ServiceOutputInline(admin.TabularInline, ):
    """ Service Submission Outputs Inlines """
    model = SubmissionOutput
    # form = ServiceOutputForm
    show_change_link = False
    extra = 0
    sortable_field_name = "order"
    sortable_options = []
    fk_name = 'submission'
    fields = ['name', 'file_pattern', 'optional', 'from_input']
    verbose_name_plural = "Outputs"
    classes = ('grp-collapse', 'grp-closed', 'collapse')


class SampleDependentInputInline(admin.TabularInline):
    model = SampleDepParam
    fk_name = 'submission'
    extra = 0
    classes = ('grp-collapse grp-closed', 'collapse')

    def has_add_permission(self, request):
        if request.current_obj is not None and request.current_obj.submission_inputs.instance_of(FileInput).count() > 0:
            return True
        return False


class ExitCodeInline(admin.TabularInline):
    model = SubmissionExitCode
    extra = 0
    fk_name = 'submission'
    is_nested = False
    classes = ('grp-collapse grp-closed', 'collapse')
    sortable_options = []


class OrganizeInputInline(SortableInlineAdminMixin, admin.TabularInline):
    model = BaseParam
    fields = ['name', 'default', 'class_label', 'related_to', 'order']
    readonly_fields = ['class_label', 'related_to']
    classes = ('grp-collapse grp-closed', 'collapse')
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

    class TextParamInline(PolymorphicInputInlineChild):
        model = TextParam
        exclude = ['order']
        verbose_name = "Text param"
        verbose_name_plural = "Text params"

    def get_formset(self, request, obj=None, **kwargs):
        print "overhere ?"
        return super(SubmitInputsInline, self).get_formset(request, obj, **kwargs)

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


class FileInputSampleInline(TabularInline):
    model = FileInputSample
    extra = 0
    fk_name = 'submission'
    verbose_name = "File Sample"
    verbose_name_plural = "Files samples"
    classes = ('grp-collapse grp-closed', 'collapse')

    def has_add_permission(self, request):
        if request.current_obj is not None and request.current_obj.submission_inputs.instance_of(FileInput).count() > 0:
            return True
        return False


class RepeatGroupAdmin(WavesModelAdmin):
    # readonly_fields = ['submission']
    # readonly_fields = ['submission']
    exclude = ['submission', ]


class OrgRepeatGroupInline(CompactInline):
    model = RepeatedGroup
    extra = 0
    verbose_name = "Input group"
    verbose_name_plural = "Organize Groups"
    classes = ('grp-collapse grp-closed', 'collapse')


class ServiceSubmissionAdmin(PolymorphicInlineSupportMixin, WavesModelAdmin):
    """ Submission process administration -- Model Submission """

    class Media:
        js = ('waves/admin/js/services.js',)

    inlines = [
        SubmitInputsInline,
        OrgRepeatGroupInline,
        ExitCodeInline,
        OrganizeInputInline,
        ServiceOutputInline,
        FileInputSampleInline,
        SampleDependentInputInline,
    ]

    def get_inline_formsets(self, request, formsets, inline_instances, obj=None):
        return super(ServiceSubmissionAdmin, self).get_inline_formsets(request, formsets, inline_instances, obj)
        """polymorphs = []
        nested = []
        standards = []
        for inline_instance in inline_instances:

            if isinstance(inline_instance, PolymorphicInlineModelAdmin):
                print "added to polymorph ", inline_instance
                polymorphs.append(inline_instance)
            elif isinstance(inline_instance, nested_admin.NestedStackedInline):
                print "added to nested ", inline_instance
                nested.append(inline_instance)
            else:
                print "added to standard ", inline_instance
                standards.append(inline_instance)
        polymorph_formsets = PolymorphicInlineSupportMixin.get_inline_formsets(self, request, formsets, polymorphs, obj)
        nested_formsets = nested_admin.NestedModelAdmin.get_inline_formsets(self, request, formsets, nested, obj)
        std_formsets = admin.ModelAdmin.get_inline_formsets(self, request, formsets, standards, obj)
        return polymorph_formsets + nested_formsets
        """

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
            ExitCodeInline
        ))
    ]

    def get_form(self, request, obj=None, **kwargs):
        request.current_obj = obj
        return super(ServiceSubmissionAdmin, self).get_form(request, obj, **kwargs)

    #    def has_module_permission(self, request):
    #        return False

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
