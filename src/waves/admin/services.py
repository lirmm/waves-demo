from __future__ import unicode_literals

import nested_inline.admin as nested_admin
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.template.defaultfilters import truncatechars
from django.utils.safestring import mark_safe
from jet.admin import CompactInline
from mptt.admin import MPTTModelAdmin

from base import WavesTabbedModelAdmin, ExportInMassMixin, DuplicateInMassMixin, MarkPublicInMassMixin
from waves.admin.submissions import ServiceOutputInline, ServiceSampleInline
from waves.forms.admin.services import *
from waves.forms.admin.submissions import ServiceSubmissionFormSet
from waves.models.profiles import WavesProfile
from waves.models.services import *
from waves.models.submissions import *


class ServiceMetaInline(CompactInline):
    model = ServiceMeta
    form = ServiceMetaForm
    sortable = 'order'
    extra = 0
    suit_classes = 'suit-tab suit-tab-metas'
    classes = ('grp-collapse grp-open',)
    fields = ['type', 'title', 'value', 'description', 'order']
    sortable_field_name = "order"
    sortable_options = []
    is_nested = False


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
    extra = 0
    fk_name = 'service'
    sortable = 'order'
    sortable_field_name = "order"
    classes = ('grp-collapse', 'grp-open')
    fields = ['label', 'available_online', 'available_api']
    show_change_link = True
    # inlines = [ServiceInputInline, ]


class ServiceAdmin(nested_admin.NestedModelAdmin, ExportInMassMixin, DuplicateInMassMixin, MarkPublicInMassMixin,
                   WavesTabbedModelAdmin):
    """ Service model objects Admin"""
    inlines = (
        ServiceRunnerParamInLine,
        ServiceSubmissionInline,
        ServiceMetaInline,
        ServiceExitCodeInline,
    )
    change_form_template = 'admin/waves/service/' + WavesTabbedModelAdmin.admin_template
    form = ServiceForm
    filter_horizontal = ['restricted_client']
    readonly_fields = ['created', 'updated', 'submission_link']
    list_display = ('name', 'api_name', 'run_on', 'api_on', 'web_on', 'version', 'category', 'status', 'created_by',
                    'submission_link')
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
            'fields': ['run_on', ],
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

    def submission_link(self, obj):
        return mark_safe('<a href="{}?service__id__exact={}">Submissions ({})</a>'.format(
            reverse("admin:waves_servicesubmission_changelist"),
            obj.id, obj.submissions.count()))

    submission_link.short_description = 'Submissions'

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

