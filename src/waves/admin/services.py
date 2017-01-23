from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.template.defaultfilters import truncatechars
from mptt.admin import MPTTModelAdmin

from base import ExportInMassMixin, DuplicateInMassMixin, MarkPublicInMassMixin
from waves.admin.submissions import *
from waves.compat import CompactInline
from waves.models.adaptors import AdaptorInitParam
from waves.models.metas import *
from waves.admin.forms.services import ServiceForm
from waves.models.services import *
from waves.models.submissions import *


User = get_user_model()

__all__ = ['ServiceAdmin', 'ServiceCategoryAdmin']


class ServiceMetaInline(CompactInline):
    model = ServiceMeta
    # form = ServiceMetaForm
    exclude = ['order',]
    extra = 0
    suit_classes = 'suit-tab suit-tab-metas'
    classes = ('grp-collapse grp-closed', 'collapse')
    fields = ['type', 'title', 'value', 'description']
    # sortable_field_name = "order"
    # sortable_options = []


class ServiceRunnerParamInLine(GenericTabularInline):
    model = AdaptorInitParam
    # form = ServiceRunnerParamForm
    fields = ['name', 'value', 'prevent_override']
    extra = 0
    classes = ('grp-collapse grp-closed', 'collapse')
    suit_classes = 'suit-tab suit-tab-adaptor'
    can_delete = False
    readonly_fields = ['name']
    is_nested = False
    sortable_options = []
    verbose_name = 'Execution param'
    verbose_name_plural = "Execution parameters"

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


class ServiceSubmissionInline(admin.TabularInline):
    """ Service Submission Inline (included in ServiceAdmin) """
    model = Submission
    extra = 0
    fk_name = 'service'
    sortable = 'order'
    sortable_field_name = "order"
    classes = ('grp-collapse grp-closed', 'collapse')
    fields = ['label', 'override_runner', 'availability', 'api_name']
    readonly_fields = ['api_name']
    show_change_link = True

    def get_extra(self, request, obj=None, **kwargs):
        if obj is None:
            return 1
        return super(ServiceSubmissionInline, self).get_extra(request, obj, **kwargs)

        # inlines = [SubmissionParamInline, ]



@admin.register(Service)
class ServiceAdmin(ExportInMassMixin, DuplicateInMassMixin, MarkPublicInMassMixin, WavesModelAdmin):
    """ Service model objects Admin"""

    class Media(WavesModelAdmin):
        js = ('waves/admin/js/services.js',)

    inlines = (
        ServiceRunnerParamInLine,
        ServiceSubmissionInline,
        ServiceMetaInline,
    )

    change_form_template = 'admin/waves/service/' + WavesModelAdmin.admin_template
    form = ServiceForm
    filter_horizontal = ['restricted_client']
    readonly_fields = ['remote_service_id', 'created', 'updated', 'submission_link']
    list_display = ('name', 'api_name', 'runner', 'version', 'category', 'status', 'created_by',
                    'submission_link')
    list_filter = ('status', 'name', 'runner', 'category', 'created_by')

    fieldsets = (
        ('General', {
            'classes': ('grp-collapse grp-closed', 'collapse'),
            'fields': ['category', 'name', 'created_by', 'runner', 'version', 'api_on', 'web_on', 'email_on']
        }),
        ('Accesses', {
            'classes': ('grp-collapse grp-closed', 'collapse'),
            'fields': ['status', 'restricted_client', ]
        }),
        ('Details', {
            'classes': ('grp-collapse grp-closed', 'collapse'),
            'fields': ['api_name', 'short_description', 'description', 'edam_topics',
                       'edam_operations', 'remote_service_id', 'created', 'updated', ]
        }),
    )

    def add_view(self, request, form_url='', extra_context=None):
        print "in add view"
        context = extra_context or {}
        context['show_save_as_new'] = False
        context['show_save_and_add_another'] = False
        context['show_save'] = False
        # self.inlines = ()
        return super(ServiceAdmin, self).add_view(request, form_url, context)

    def get_inline_instances(self, request, obj=None):
        print "in get inlines ", obj
        if obj is None:
            return []
        return super(ServiceAdmin, self).get_inline_instances(request, obj)

    def submission_link(self, obj):
        links = []
        for submission in obj.submissions.all():
            links.append(
                '<a href="{}">Submission ({})</a>'.format(
                    reverse("admin:waves_submission_change", args=[submission.pk]),
                    submission.label))
        return mark_safe("<br/>".join(links))

    submission_link.short_description = 'Submissions'

    def get_readonly_fields(self, request, obj=None):
        """ Set up readonly fields according to user profile """
        readonly_fields = super(ServiceAdmin, self).get_readonly_fields(request, obj)
        if not request.user.is_superuser:
            readonly_fields.append('created_by')
        if obj is not None and obj.created_by != request.user:
            readonly_fields.append('api_name')
            readonly_fields.append('clazz')
            readonly_fields.append('version')
        return readonly_fields

    def get_form(self, request, obj=None, **kwargs):
        """ Assign current obj to form """
        request.current_obj = obj
        form = super(ServiceAdmin, self).get_form(request, obj, **kwargs)
        form.current_user = request.user
        # form.base_fields['runner'].widget.can_add_related = False
        form.base_fields['runner'].widget.can_delete_related = False
        return form

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        """ Filter runner and created_by list """
        if db_field.name == "created_by":
            kwargs['queryset'] = User.objects.filter(is_staff=True)
        return super(ServiceAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(MPTTModelAdmin):
    """ Model admin for ServiceCategory model objects"""
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
