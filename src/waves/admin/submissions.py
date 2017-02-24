""" Service Submission administration classes """
from __future__ import unicode_literals

from adminsortable2.admin import SortableInlineAdminMixin
from django.contrib import admin
from django.utils.safestring import mark_safe
from polymorphic.admin import PolymorphicInlineSupportMixin

from waves.admin.adaptors import SubmissionRunnerParamInLine
from waves.admin.base import WavesModelAdmin, DynamicInlinesAdmin
from waves.admin.forms.services import SampleDepForm, InputInlineForm, InputSampleForm, SubmissionForm
from waves.compat import CompactInline
from waves.models.inputs import *
from waves.models.submissions import *
from waves.utils import url_to_edit_object


class SubmissionOutputInline(CompactInline):
    """ Service Submission Outputs Inlines """
    model = SubmissionOutput
    # form = ServiceOutputForm
    show_change_link = False
    extra = 0
    sortable_field_name = "order"
    sortable_options = []
    fk_name = 'submission'
    fields = ['label', 'file_pattern', 'from_input', 'help_text', 'edam_format', 'edam_data']
    verbose_name_plural = "Outputs"
    classes = ('grp-collapse', 'grp-closed', 'collapse')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "from_input":
            kwargs['queryset'] = AParam.objects.filter(submission=request.current_obj)
        return super(SubmissionOutputInline, self).formfield_for_foreignkey(db_field, request, **kwargs)


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
            kwargs['queryset'] = BaseParam.objects.filter(submission=request.current_obj,
                                                          cmd_format__gt=0).not_instance_of(FileInput)
        elif db_field.name == "sample":
            kwargs['queryset'] = FileInputSample.objects.filter(submission=request.current_obj)
        return super(SampleDependentInputInline, self).formfield_for_foreignkey(db_field, request, **kwargs)


class ExitCodeInline(admin.TabularInline):
    model = SubmissionExitCode
    extra = 0
    fk_name = 'submission'
    is_nested = False
    classes = ('grp-collapse grp-closed', 'collapse')
    sortable_options = []


class OrganizeInputInline(SortableInlineAdminMixin, admin.TabularInline):
    model = AParam
    form = InputInlineForm
    fields = ['label', 'class_label', 'name', 'required', 'cmd_format', 'default', 'step', 'order']
    readonly_fields = ['class_label', 'step', 'aparam_ptr']
    classes = ('grp-collapse', 'grp-closed', 'collapse', 'show-change-link-popup')
    can_delete = True
    extra = 0
    show_change_link = True
    list_per_page = 5

    def class_label(self, obj):
        if obj.parent:
            level = 0
            init = obj.parent
            while init:
                level += 1
                init = init.parent
            return mark_safe("<span class='icon-arrow-right'></span>" * level +
                             "%s (%s:%s)" % (obj._meta.verbose_name, obj.parent.name, obj.when_value))
        return obj._meta.verbose_name

    class_label.short_description = "Input type"

    def get_queryset(self, request):
        # TODO order fields according to related also (display first level items just followed by their dependents)
        return super(OrganizeInputInline, self).get_queryset(request).not_instance_of(FileInputSample).order_by(
            '-required', 'tree_id', 'lft', 'order')

    def step(self, obj):
        if hasattr(obj, 'step'):
            return obj.step
        else:
            return 'N/A'


class FileInputSampleInline(CompactInline):
    model = FileInputSample
    form = InputSampleForm
    extra = 0
    fk_name = 'file_input'
    fields = ['label', 'file', 'file_input']
    exclude = ['order']
    readonly_fields = ['aparam_ptr']
    classes = ('grp-collapse grp-closed', 'collapse')

    """def has_add_permission(self, request):
        if request.current_obj is not None and request.current_obj.submission_inputs.instance_of(FileInput).count() > 0:
            return True
        return False
"""
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """if db_field.name == "file_input":
            kwargs['queryset'] = FileInput.objects.filter(submission=request.current_obj)
        """
        return super(FileInputSampleInline, self).formfield_for_foreignkey(db_field, request, **kwargs)


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
class ServiceSubmissionAdmin(PolymorphicInlineSupportMixin, WavesModelAdmin, DynamicInlinesAdmin):
    """ Submission process administration -- Model Submission """
    current_obj = None
    form = SubmissionForm
    exclude = ['order']
    save_on_top = True
    list_display = ['get_name', 'service_link', 'runner_link', 'available_online', 'available_api', 'runner']
    readonly_fields = ['available_online', 'available_api']
    list_filter = (
        'service__name',
        'availability'
    )
    search_fields = ('service__name', 'label', 'override_runner__name', 'service__runner__name')
    fieldsets = [
        ('General', {
            'fields': ['service', 'name', 'availability', 'api_name', 'runner', ],
            'classes': ['collapse']
        }),
    ]
    show_full_result_count = True

    def get_inlines(self, request, obj=None):
        _inlines = [
            OrganizeInputInline,
            # OrgRepeatGroupInline,
            SubmissionOutputInline,
            # FileInputSampleInline,
            SampleDependentInputInline,
            ExitCodeInline,
        ]
        self.inlines = _inlines
        if obj.runner is not None and obj.runner.adaptor_params.filter(prevent_override=False).count() > 0:
            self.inlines.append(SubmissionRunnerParamInLine)
        return self.inlines

    def get_model_perms(self, request):
        return super(ServiceSubmissionAdmin, self).get_model_perms(request)

    def add_view(self, request, form_url='', extra_context=None):
        context = extra_context or {}
        context['show_save_as_new'] = False
        context['show_save_and_add_another'] = False
        context['show_save'] = False
        return super(ServiceSubmissionAdmin, self).add_view(request, form_url, context)

    def get_form(self, request, obj=None, **kwargs):
        request.current_obj = obj
        form = super(ServiceSubmissionAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['runner'].widget.can_add_related = False
        form.base_fields['runner'].widget.can_change_related = False
        form.base_fields['runner'].widget.can_delete_related = False
        form.base_fields['runner'].required = False
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
        return url_to_edit_object(obj.service)

    def get_name(self, obj):
        return mark_safe("<span title='Edit submission'>%s (%s)</span>" % (obj.name, obj.service))

    service_link.short_description = "Service"
    get_name.short_description = "Name"

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super(ServiceSubmissionAdmin, self).get_readonly_fields(request, obj))
        if obj is not None:
            readonly_fields.append('service')
        return readonly_fields

    def available_api(self, obj):
        return obj.available_api

    def available_online(self, obj):
        return obj.available_online

    def save_model(self, request, obj, form, change):
        if not obj.runner:
            obj.adaptor_params.all().delete()
        super(ServiceSubmissionAdmin, self).save_model(request, obj, form, change)

    def has_add_permission(self, request):
        return False

    def runner_link(self, obj):
        return url_to_edit_object(obj.get_runner())
