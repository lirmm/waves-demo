from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.admin import ModelAdmin, TabularInline

import waves.const as const
from waves.forms.admin import JobInputForm, JobOutputForm, JobForm
from waves.models import JobInput, JobOutput, JobHistory, Job


class JobInputInline(TabularInline):
    model = JobInput
    form = JobInputForm
    extra = 0
    suit_classes = 'suit-tab suit-tab-inputs'
    exclude = ('order',)
    readonly_fields = ('name', 'value')
    can_delete = False
    ordering = ('order',)
    fields = ('name', 'value')

    def has_add_permission(self, request):
        return False


class JobOutputInline(TabularInline):
    model = JobOutput
    form = JobOutputForm
    extra = 0
    suit_classes = 'suit-tab suit-tab-outputs'
    can_delete = False
    readonly_fields = ('label', 'name', 'value')
    ordering = ('order',)
    fields = ('label', 'name', 'value')

    def has_add_permission(self, request):
        return False


class JobHistoryInline(TabularInline):
    model = JobHistory
    suit_classes = 'suit-tab suit-tab-history'
    readonly_fields = ('status', 'timestamp', 'message')
    can_delete = False
    extra = 0

    def has_add_permission(self, request):
        return False


class JobAdmin(ModelAdmin):
    model = Job
    form = JobForm
    inlines = [
        JobInputInline,
        JobOutputInline,
        JobHistoryInline
    ]
    list_filter = ('status', 'service')
    list_display = ('__str__', 'status', 'client', 'service', 'get_run_on', 'created', 'updated')

    list_per_page = 30
    suit_form_tabs = (('general', 'General'), ('inputs', 'Inputs'), ('outputs', 'Outputs'), ('history', 'History'))
    readonly_fields = ('slug', 'email_to', 'service', 'status', 'created', 'updated', 'get_run_on')
    fieldsets = [
        (None, {
            'classes': ('suit-tab', 'suit-tab-general',),
            'fields': ['service', 'status', 'created', 'updated', 'client', 'email_to', 'slug', 'get_run_on']
        }
         ),

    ]

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
        return super(JobAdmin, self).get_form(request, obj, **kwargs)

    def get_run_on(self, obj):
        return obj.service.run_on.name

    get_run_on.short_description = 'Run on'

admin.site.register(Job, JobAdmin)