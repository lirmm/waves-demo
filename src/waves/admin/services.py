from __future__ import unicode_literals

import nested_admin
from os.path import join
import json
from django.contrib import admin, messages
from django.template.defaultfilters import truncatechars
from django.contrib.admin import StackedInline
from grappelli.forms import GrappelliSortableHiddenMixin
from mptt.admin import MPTTModelAdmin
from django.forms.models import BaseInlineFormSet
from django.core.exceptions import ValidationError
import waves.const
from base import WavesTabbedModelAdmin, ExportInMassMixin, DuplicateInMassMixin, MarkPublicInMassMixin
from waves.forms.admin.services import *
from waves.models.services import *
from waves.models.runners import Runner
from waves.models.samples import *
from waves.models.profiles import WavesProfile


class ServiceMetaInline(GrappelliSortableHiddenMixin, admin.TabularInline):
    model = ServiceMeta
    form = ServiceMetaForm
    sortable = 'order'
    extra = 1
    suit_classes = 'suit-tab suit-tab-metas'
    classes = ('grp-collapse grp-open',)
    fields = ['type', 'title', 'value', 'description', 'order']
    sortable_field_name = "order"
    is_nested = False


class ServiceOutputFromInputFormset(BaseInlineFormSet):
    def clean(self):
        try:
            forms = [f for f in self.forms
                     if f.cleaned_data
                     and not f.cleaned_data.get('DELETE', False)]
            # print "cleandformset ", self.instance.srv_input, ", mandatory ", self.instance.srv_input.mandatory, ', default ', self.instance.srv_input.default
            if self.instance.file_pattern and self.instance.from_input:
                if len(forms) < self.instance.service.submissions.count():
                    raise ValidationError('You must setup an value for all possible submission')
                elif len(forms) < self.instance.service.submissions.count():
                    raise ValidationError('You can not provide more origin than possible submissions')
                else:
                    f_submission = set(f.instance.submission for f in forms)
                    s_submission = set(s for s in self.instance.service.submissions.all())
                    if not f_submission.__eq__(s_submission):
                        raise ValidationError('Misconfiguration for origins, check your data')
        except AttributeError:
            pass


class ServiceOutputFromInputInline(nested_admin.NestedTabularInline):
    model = ServiceOutputFromInputSubmission
    form = ServiceOutputFromInputSubmissionForm
    formset = ServiceOutputFromInputFormset
    fields = ['submission', 'srv_input', ]
    fk_name = 'srv_output'
    verbose_name = "Valuated from"
    verbose_name_plural = "Output is valuated from an input"
    extra = 2

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'submission' and request.current_obj is not None:
            kwargs['queryset'] = ServiceSubmission.objects.filter(service=request.current_obj)
        return super(ServiceOutputFromInputInline, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def get_extra(self, request, obj=None, **kwargs):
        if obj is not None:
            return int(obj.service.submissions.count() - obj.from_input_submission.count())
        else:
            if request.current_obj:
                return request.current_obj.submissions.count()
        # By default we return only one extra (setup with only one available submission form)
        return 1


class ServiceOutputInline(GrappelliSortableHiddenMixin, nested_admin.NestedStackedInline, admin.TabularInline):
    model = ServiceOutput
    form = ServiceOutputForm
    sortable = 'order'
    extra = 0
    classes = ('grp-collapse grp-open',)
    sortable_field_name = "order"
    fk_name = 'service'
    fields = ['name', 'file_pattern', 'short_description', 'may_be_empty', 'from_input', 'order']
    verbose_name_plural = "Service outputs"
    inlines = [ServiceOutputFromInputInline, ]

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'from_input' and request.current_obj is not None:
            kwargs['queryset'] = ServiceInput.objects.filter(service=request.current_obj.default_submission,
                                                             mandatory=True)
        return super(ServiceOutputInline, self).formfield_for_foreignkey(db_field, request, **kwargs)


class ServiceRunnerParamInLine(admin.TabularInline):
    model = ServiceRunnerParam
    form = ServiceRunnerParamForm
    fields = ['param', '_value', 'param_default']
    extra = 0
    suit_classes = 'suit-tab suit-tab-adaptor'
    can_delete = False
    readonly_fields = ['param', 'param_default']
    is_nested = False

    def param_default(self, obj):
        return obj.param.default if obj.param.default else '--'

    def get_max_num(self, request, obj=None, **kwargs):
        if obj is not None:
            return self.get_queryset(request).count()
        else:
            return 0

    def get_min_num(self, request, obj=None, **kwargs):
        if obj is not None:
            return self.get_queryset(request).count()
        else:
            return 0

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return request.current_obj is not None

    def get_queryset(self, request):
        qs = super(ServiceRunnerParamInLine, self).get_queryset(request)
        try:
            parent_obj_id = request.resolver_match.args[0]
            return qs.filter(param__prevent_override=False, service_id=parent_obj_id)
        except IndexError:
            return qs


class ServiceSampleDependentInputInline(GrappelliSortableHiddenMixin, admin.TabularInline):
    model = ServiceSampleDependentsInput
    fk_name = 'sample'
    extra = 0
    sortable_field_name = "order"


class ServiceSampleInline(nested_admin.NestedTabularInline):
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


class ServiceInputInline(GrappelliSortableHiddenMixin, nested_admin.NestedStackedInline):
    model = ServiceInput
    form = ServiceInputForm
    sortable = 'order'
    extra = 0
    fk_name = 'service'
    classes = ('grp-collapse', 'grp-open')
    inlines = [RelatedInputInline, ]
    sortable_field_name = "order"
    verbose_name = 'Input'
    verbose_name_plural = "Inputs"

    def get_queryset(self, request):
        qs = super(ServiceInputInline, self).get_queryset(request)
        return qs  # .instance_of(ServiceInput)


class ServiceExitCodeInline(admin.TabularInline):
    model = ServiceExitCode
    extra = 1
    fk_name = 'service'
    is_nested = False
    classes = ('grp-collapse', 'grp-open')


class ServiceSubmissionInline(GrappelliSortableHiddenMixin, nested_admin.NestedStackedInline):
    """ Service Submission Inline """
    model = ServiceSubmission
    form = ServiceSubmissionForm
    formset = ServiceSubmissionFormSet
    extra = 0
    fk_name = 'service'
    sortable = 'order'
    sortable_field_name = "order"
    classes = ('grp-collapse', 'grp-open')
    fields = ['label', 'available_online', 'available_api', 'api_name', "order"]
    inlines = [ServiceInputInline, ]


class ServiceAdmin(nested_admin.NestedModelAdmin, ExportInMassMixin, DuplicateInMassMixin, MarkPublicInMassMixin,
                   WavesTabbedModelAdmin):
    """ Service model objects Admin"""
    inlines = (
        ServiceRunnerParamInLine,
        ServiceSubmissionInline,
        ServiceOutputInline,
        ServiceMetaInline,
        ServiceExitCodeInline,
        ServiceSampleInline,
    )
    change_form_template = 'admin/waves/service/' + WavesTabbedModelAdmin.admin_template
    form = ServiceForm
    filter_horizontal = ['restricted_client']
    readonly_fields = ['created', 'updated']
    list_display = ('name', 'api_name', 'run_on', 'api_on', 'web_on', 'version', 'category', 'status', 'created_by', 'updated')
    list_filter = ('status', 'name', 'run_on', 'category', 'created_by')
    tab_overview = (
        (None, {
            'fields': ['category', 'name', 'status', 'version',
                       'short_description', 'description']
        }),
    )
    tab_details = (
        (None, {
            'fields': ['api_name', 'created_by', 'restricted_client', 'email_on', 'api_on', 'web_on', 'created',
                       'updated']
            # TODO reintegrate 'clazz'
        }),
    )
    tab_runner = (
        (None, {
            'fields': ['run_on', ]
        }),
        ServiceRunnerParamInLine,
    )
    tab_submission = (ServiceSubmissionInline,)
    tab_outputs = (
        ServiceOutputInline,
        ServiceExitCodeInline)
    tab_metas = (ServiceMetaInline,)
    tab_samples = (ServiceSampleInline,)
    tabs = [
        ('General', tab_overview),
        ('Details', tab_details),
        ('Metas', tab_metas),
        ('Run configuration', tab_runner),
        ('Submissions', tab_submission),
        ('Outputs', tab_outputs),
        ('Samples', tab_samples)
    ]

    def get_readonly_fields(self, request, obj=None):
        """ Set up readonly fields according to user profile """
        readonly_fields = super(ServiceAdmin, self).get_readonly_fields(request, obj)
        if not request.user.is_superuser:
            readonly_fields.append('created_by')
        if obj is not None and obj.created_by != request.user.profile:
            readonly_fields.append('api_name')
            readonly_fields.append('clazz')
            readonly_fields.append('version')
        return readonly_fields

    def get_form(self, request, obj=None, **kwargs):
        """ Assign current obj to form """
        request.current_obj = obj
        form = super(ServiceAdmin, self).get_form(request, obj, **kwargs)
        form.current_user = request.user
        return form

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        """ Filter runner and created_by list """
        if db_field.name == 'run_on':
            kwargs['queryset'] = Runner.objects.filter(available=True)
        elif db_field.name == "created_by":
            kwargs['queryset'] = WavesProfile.objects.filter(user__is_staff=True)
        return super(ServiceAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class ServiceCategoryAdmin(GrappelliSortableHiddenMixin, MPTTModelAdmin):
    """ Model admin for ServiceCategory model objects"""
    form = ServiceCategoryForm
    list_display = ('name', 'parent', 'api_name', 'short', 'ref')
    sortable_field_name = 'order'
    sortable_field_name = "order"
    mptt_indent_field = 'name'

    def short(self, obj):
        """ Truncate short description in list display """
        return truncatechars(obj.short_description, 100)


admin.site.register(Service, ServiceAdmin)
admin.site.register(ServiceCategory, ServiceCategoryAdmin)
