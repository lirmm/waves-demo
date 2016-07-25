from __future__ import unicode_literals

from django.contrib import admin, messages
from django.contrib.admin import ModelAdmin, TabularInline
from tabbed_admin import TabbedModelAdmin

import waves.const as const
from waves.forms.admin import JobInputForm, JobOutputForm, JobForm
from waves.models import JobInput, JobOutput, JobHistory, Job


class JobInputInline(TabularInline):
    model = JobInput
    form = JobInputForm
    extra = 0
    suit_classes = 'suit-tab suit-tab-inputs'
    exclude = ('order',)
    readonly_fields = ('name', 'value','srv_input')
    can_delete = False
    ordering = ('order',)
    fields = ('srv_input', 'name', 'value', )

    def has_add_permission(self, request):
        return False

    def get_srv_input(self, obj):
        return obj.srv_input.label


class JobOutputInline(TabularInline):
    model = JobOutput
    form = JobOutputForm
    extra = 0
    suit_classes = 'suit-tab suit-tab-outputs'
    can_delete = False
    readonly_fields = ('name', 'value')
    ordering = ('order',)
    fields = ('name', 'value')
    # classes = ('grp-collapse grp-closed',)

    def has_add_permission(self, request):
        return False


class JobHistoryInline(TabularInline):
    model = JobHistory
    suit_classes = 'suit-tab suit-tab-history'
    # classes = ('grp-collapse grp-closed',)
    verbose_name_plural = "Job history"

    readonly_fields = ('status', 'timestamp', 'message')
    can_delete = False
    extra = 0

    def has_add_permission(self, request):
        return False


def mark_rerun(modeladmin, request, queryset):
    for srv in queryset.all():
        try:
            srv.status = const.JOB_CREATED
            srv.save()
            messages.add_message(request, level=messages.SUCCESS, message="Jobs %s successfully marked for re-run" % srv)
        except StandardError as e:
            messages.add_message(request, level=messages.ERROR, message="Job %s error %s " % (srv, e.message))

mark_rerun.short_description = "Re-run jobs"


class JobAdmin(TabbedModelAdmin, ModelAdmin):
    class Media:
        css = {
            'all': ('tabbed_admin/css/tabbed_admin.css',)
        }
    model = Job
    form = JobForm
    inlines = [
        JobHistoryInline,
        JobInputInline,
        JobOutputInline,
    ]
    actions = [mark_rerun, ]
    list_filter = ('status', 'service', 'client')
    list_display = ('__str__', 'get_colored_status', 'client', 'service', 'get_run_on', 'created', 'updated')
    list_per_page = 30

    search_fields = ('client__email', 'service__name', 'service__run_on__clazz', 'service__run_on_name')

    # Suit form params (not used by default)
    suit_form_tabs = (('general', 'General'), ('inputs', 'Inputs'), ('outputs', 'Outputs'), ('history', 'History'))

    # grappelli list filter
    change_list_template = "admin/change_list_filter_sidebar.html"
    change_form_template = 'admin/waves/job/change_form.html'
    readonly_fields = ('slug', 'email_to', 'service', 'status', 'created', 'updated', 'get_run_on')

    """
    fieldsets = [
        (None, {'classes': ('suit-tab', 'suit-tab-general',),
                'fields': ['service', 'status', 'created', 'updated', 'client', 'email_to', 'slug', 'get_run_on']
                }
         ),
    ]
    """
    tab_overview = (
        (None, {
            'fields': ['service', 'status', 'created', 'updated', 'client', 'email_to', 'slug', 'get_run_on']
        }),
    )
    tab_history = (JobHistoryInline,)
    tab_inputs = (JobInputInline,)
    tab_outputs = (JobOutputInline,)
    tabs = [
        ('General', tab_overview),
        ('Job History', tab_history),
        ('Service Inputs', tab_inputs),
        ('Services outputs', tab_outputs),
    ]

    def get_list_filter(self, request):
        return super(JobAdmin, self).get_list_filter(request)

    def get_queryset(self, request):
        queryset = super(JobAdmin, self).get_queryset(request)
        # TODO add user group right filtering, default filtering
        return queryset

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser or (obj is not None and request.user == obj.client)

    def has_add_permission(self, request):
        if not request.user.is_superuser:
            return False
        return True

    def __init__(self, model, admin_site):
        super(JobAdmin, self).__init__(model, admin_site)

    def suit_row_attributes(self, obj, request):
        css_class = {
            const.JOB_COMPLETED: 'success',
            const.JOB_RUNNING: 'warning',
            const.JOB_ERROR: 'error',
            const.JOB_CANCELLED: 'error',
            const.JOB_PREPARED: 'info',
            const.JOB_CREATED: 'info',
        }.get(obj.status)
        if css_class:
            return {'class': css_class}

    def get_form(self, request, obj=None, **kwargs):
        request.current_obj = obj
        form = super(JobAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['client'].widget.can_add_related = False
        return form

    def get_run_on(self, obj):
        return obj.service.run_on.name

    def get_colored_status(self, obj):
        return obj.colored_status()

    get_colored_status.short_description = 'Status'
    get_run_on.short_description = 'Run on'


admin.site.register(Job, JobAdmin)
