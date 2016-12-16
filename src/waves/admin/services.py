from __future__ import unicode_literals

from django.template.defaultfilters import truncatechars
from mptt.admin import MPTTModelAdmin

from base import ExportInMassMixin, DuplicateInMassMixin, MarkPublicInMassMixin
from waves.admin.submissions import *
from waves.admin.submissions import ServiceExitCodeInline
from waves.forms.admin.services import *
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
    fields = ['type', 'order', 'title', 'value', 'description']
    sortable_field_name = "order"
    sortable_options = []


class ServiceRunnerParamInLine(admin.TabularInline):
    model = ServiceRunParam
    form = ServiceRunnerParamForm
    fields = ['name', 'value']
    extra = 0
    suit_classes = 'suit-tab suit-tab-adaptor'
    can_delete = False
    readonly_fields = ['name']
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
        return super(ServiceRunnerParamInLine, self).get_queryset(request).filter(prevent_override=False)


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
    # inlines = [SubmissionParamInline, ]


class ServiceAdmin(ExportInMassMixin, DuplicateInMassMixin, MarkPublicInMassMixin, WavesTabbedModelAdmin):
    """ Service model objects Admin"""
    inlines = (
        ServiceRunnerParamInLine,
        ServiceSubmissionInline,
        ServiceMetaInline,
    )
    change_form_template = 'admin/waves/service/' + WavesTabbedModelAdmin.admin_template
    form = ServiceForm
    filter_horizontal = ['restricted_client']
    readonly_fields = ['remote_service_id', 'created', 'updated', 'submission_link']
    list_display = ('name', 'api_name', 'runner', 'api_on', 'web_on', 'version', 'category', 'status', 'created_by',
                    'submission_link')
    list_filter = ('status', 'name', 'runner', 'category', 'created_by')

    fieldsets = (
        ('General', {
            'fields': ['category', 'name', 'created_by', 'status', 'runner', 'version', 'api_on', 'web_on', 'email_on']
        }),
        ('Details', {
            'fields': ['api_name', 'short_description', 'description', 'restricted_client', 'edam_topics',
                       'edam_operations', 'remote_service_id', 'created', 'updated', ]
        }),
    )

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
