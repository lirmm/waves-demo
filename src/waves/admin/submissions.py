""" Service Submission administration classes """
from __future__ import unicode_literals

from adminsortable2.admin import SortableInlineAdminMixin
from django.contrib import admin
from django.utils.safestring import mark_safe

from waves.admin.base import WavesModelAdmin
from waves.admin.forms.services import SampleDepForm, InputInlineForm, InputSampleForm
from waves.compat import CompactInline
from waves.models.inputs import *
from waves.models.samples import *
from waves.models.submissions import *


# TODO enable the standard django layout for polymorphic inlines


class SubmissionOutputInline(CompactInline):
    """ Service Submission Outputs Inlines """
    model = SubmissionOutput
    # form = ServiceOutputForm
    show_change_link = False
    extra = 0
    sortable_field_name = "order"
    sortable_options = []
    fk_name = 'submission'
    fields = ['label', 'api_name', 'file_pattern', 'from_input', 'help_text', 'edam_format', 'edam_data']
    verbose_name_plural = "Outputs"
    classes = ('grp-collapse', 'grp-closed', 'collapse')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "from_input":
            kwargs['queryset'] = AParam.objects.filter(submission=request.current_obj)
        return super(SubmissionOutputInline, self).formfield_for_foreignkey(db_field, request, **kwargs)


class SampleDependentInputInline(CompactInline):
    model = SampleDepParam
    form = SampleDepForm
    fk_name = 'file_input'
    extra = 0
    classes = ('grp-collapse grp-closed', 'collapse')

    def has_add_permission(self, request):
        if request.current_obj is not None and request.current_obj.sample_dependencies.count() > 0:
            return True
        return False

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "related_to" and request.current_obj is not None:
            kwargs['queryset'] = AParam.objects.filter(submission=request.current_obj.submission,
                                                       cmd_format__gt=0).not_instance_of(FileInput)
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
                             "%s (%s)" % (obj._meta.verbose_name, obj.when_value))
        return obj._meta.verbose_name

    class_label.short_description = "Input type"

    def get_queryset(self, request):
        # TODO order fields according to related also (display first level items just followed by their dependents)
        return super(OrganizeInputInline, self).get_queryset(request).order_by('-required', 'tree_id', 'lft', 'order')

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
    classes = ('grp-collapse grp-closed', 'collapse')


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


