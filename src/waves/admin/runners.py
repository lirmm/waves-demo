"""
Admin pages for Runner and RunnerParam models objects
"""
from __future__ import unicode_literals

from django.contrib import messages
from django.contrib.admin import register, TabularInline
from django.contrib.admin.options import IS_POPUP_VAR

from base import ExportInMassMixin
from waves.admin.adaptors import RunnerParamInline
from waves.admin.base import WavesModelAdmin
from waves.admin.forms.runners import RunnerForm
from waves.models import Runner, Service

__all__ = ['RunnerAdmin']


class ServiceRunInline(TabularInline):
    model = Service
    extra = 0
    fields = ['name', 'version', 'created', 'updated', 'created_by']
    readonly_fields = ['name', 'version', 'created', 'updated', 'created_by']
    show_change_link = True
    verbose_name_plural = "Related Services"

    def has_delete_permission(self, request, obj=None):
        """ No delete permission for runners params
        :return: False
        """
        return False

    def has_add_permission(self, request):
        """ No add permission for runners params
        :return: False
        """
        return False


@register(Runner)
class RunnerAdmin(ExportInMassMixin, WavesModelAdmin):
    """ Admin for Job Runner """
    model = Runner
    form = RunnerForm
    inlines = (RunnerParamInline, ServiceRunInline)
    list_display = ('name', 'clazz', 'short_description', 'nb_services')
    list_filter = ('name', 'clazz')
    fieldsets = [
        ('Main', {
            'fields': ['name', 'clazz', 'update_init_params']
        }),
        ('Description', {
            'fields': ['short_description', 'description'],
            'classes': ('collapse grp-collapse grp-closed',),
        }),
    ]

    def add_view(self, request, form_url='', extra_context=None):
        context = extra_context or {}
        context['show_save_as_new'] = IS_POPUP_VAR in request.GET
        context['show_save_and_add_another'] = False
        context['show_save'] = IS_POPUP_VAR in request.GET
        return super(RunnerAdmin, self).add_view(request, form_url, context)

    def nb_services(self, obj):
        return obj.runs.count()

    nb_services.short_description = "Running Services"

    def save_model(self, request, obj, form, change):
        """ Add related Service / Jobs updates upon Runner modification """
        super(RunnerAdmin, self).save_model(request, obj, form, change)
        if obj is not None and ('update_init_params' in form.changed_data or 'clazz' in form.changed_data):
            if 'update_init_params' in form.changed_data:
                for service in obj.runs.all():
                    message = 'Related service %s has been reset' % service.name
                    service.status = Service.SRV_DRAFT
                    service.set_run_params_defaults()
                    service.save()
                    # TODO sometime we should save runParams directly in jobs, so won't rely on db modification
                    for job in service.running_jobs:
                        job.adaptor.cancel_job(job=job)
                        message += '<br/>- Related pending job %s has been cancelled' % job.title
                    messages.info(request, message)
