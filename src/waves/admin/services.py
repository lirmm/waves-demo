from __future__ import unicode_literals

# import nested_admin
import nested_inline.admin as nested_admin
from django.contrib import admin
from django.contrib.admin import StackedInline
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet
from django.template.defaultfilters import truncatechars
# from grappelli.forms import GrappelliSortableHiddenMixin
from mptt.admin import MPTTModelAdmin

import waves.const
from base import WavesTabbedModelAdmin, ExportInMassMixin, DuplicateInMassMixin, MarkPublicInMassMixin
from waves.forms.admin.services import *
from waves.models.profiles import WavesProfile
from waves.models.runners import Runner
from waves.models.samples import *
from waves.models.services import *
from waves.models.submissions import *
from jet.admin import CompactInline


class ServiceMetaInline(admin.TabularInline):
    model = ServiceMeta
    form = ServiceMetaForm
    sortable = 'order'
    extra = 1
    suit_classes = 'suit-tab suit-tab-metas'
    classes = ('grp-collapse grp-open',)
    fields = ['type', 'title', 'value', 'description', 'order']
    sortable_field_name = "order"
    sortable_options = []
    is_nested = False


class ServiceOutputInline(CompactInline):
    model = ServiceOutput
    form = ServiceOutputForm
    sortable = 'order'
    extra = 0
    classes = ('collapse', )
    sortable_field_name = "order"
    sortable_options = []
    fk_name = 'service'
    fields = ['name', 'file_pattern', 'short_description', 'may_be_empty', 'related_from_input', 'order']
    verbose_name_plural = "Service outputs"
    show_change_link = True

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
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
    sortable_options = []

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


class ServiceSampleDependentInputInline(admin.TabularInline):
    model = ServiceSampleDependentsInput
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


class ServiceExitCodeInline(CompactInline):
    model = ServiceExitCode
    extra = 1
    fk_name = 'service'
    is_nested = False
    classes = ('grp-collapse', 'grp-open')
    sortable_options = []


class ServiceSubmissionInline(admin.TabularInline):
    """ Service Submission Inline (included in ServiceAdmin) """
    model = ServiceSubmission
    form = ServiceSubmissionForm
    formset = ServiceSubmissionFormSet
    extra = 0
    fk_name = 'service'
    sortable = 'order'
    sortable_field_name = "order"
    classes = ('grp-collapse', 'grp-open')
    fields = ['label', 'available_online', 'available_api']
    show_change_link = True
    # inlines = [ServiceInputInline, ]


class ServiceSubmissionAdmin(WavesTabbedModelAdmin):
    inlines = [ServiceInputInline]
    list_display = ['label' ,
                    'available_online' ,
                    'available_api' ,
                    'service' ,]


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
    list_display = ('name', 'api_name', 'run_on', 'api_on', 'web_on', 'version', 'category', 'status', 'created_by',
                    'updated')
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
    fieldsets = (
        ('General', {
            'fields': ['category', 'name', 'status', 'version', 'short_description', 'description']
        }),
        ('Details', {
            'fields': ['api_name', 'created_by', 'restricted_client', 'email_on', 'api_on', 'web_on', 'created',
                       'updated']
        }),
        ('Run configuration', {
            'fields': ['run_on',],
        }),
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
        if db_field.name == "created_by":
            kwargs['queryset'] = WavesProfile.objects.filter(user__is_staff=True)
        return super(ServiceAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class ServiceCategoryAdmin(MPTTModelAdmin):
    """ Model admin for ServiceCategory model objects"""
    form = ServiceCategoryForm
    list_display = ('name', 'parent', 'api_name', 'short', 'ref')
    sortable_field_name = 'order'
    mptt_indent_field = 'name'
    fieldsets = [
        (None, {
            'fields': ['name', 'parent', 'api_name']
        }),
        ('Details', {
            'fields': ['short_description', 'description', 'ref']
        })
    ]

    def short(self, obj):
        """ Truncate short description in list display """
        return truncatechars(obj.short_description, 100)


admin.site.register(Service, ServiceAdmin)
admin.site.register(ServiceCategory, ServiceCategoryAdmin)
admin.site.register(ServiceSubmission, ServiceSubmissionAdmin)