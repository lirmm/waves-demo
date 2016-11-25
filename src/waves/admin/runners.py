"""
Admin pages for Runner and RunnerParam models objects
"""
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib import messages
from django.contrib.admin import TabularInline
from waves.forms.admin import RunnerParamForm, RunnerForm
from waves.models import RunnerParam, Runner, Job
from base import ExportInMassMixin, MarkPublicInMassMixin
import waves.const


class RunnerParamInline(TabularInline):
    """ Job Runner class instantiation parameters insertion field
    Inline are automatically generated from effective implementation class 'init_params' property """
    model = RunnerParam
    form = RunnerParamForm
    extra = 0
    fields = ['name', 'prevent_override', 'default']
    readonly_fields = ('name',)

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


class RunnerAdmin(ExportInMassMixin, MarkPublicInMassMixin):
    """ Admin for Job Runner """
    model = Runner
    form = RunnerForm
    inlines = (
        RunnerParamInline,
    )

    list_display = ('name', 'clazz', 'available', 'short_description')
    list_filter = ('name', 'available')
    fieldsets = [
        ('General', {
            'fields': ['name', 'available', 'clazz', 'description', 'update_init_params']
        }
         ),
    ]

    def save_model(self, request, obj, form, change):
        """ Add related Service / Jobs updates upon Runner modification """
        super(RunnerAdmin, self).save_model(request, obj, form, change)
        if obj is not None and ('update_init_params' in form.changed_data or 'clazz' in form.changed_data):
            if 'update_init_params' in form.changed_data:
                for service in obj.runs.all():
                    message = 'Related service %s has been reset' % service.name
                    service.status = waves.const.SRV_DRAFT
                    service.reset_default_params(obj.runner_params.all())
                    service.save()
                    # service.reset_runner_params(init_params_keys=obj.adaptor.init_params.keys())
                    jobs = Job.objects.filter(status__lte=waves.const.JOB_QUEUED, service=service)
                    for job in jobs:
                        job.adaptor.cancel_job(job=job)
                        message += '<br/>- Related pending job %s has been cancelled' % job.title
                    messages.warning(request, message)

admin.site.register(Runner, RunnerAdmin)
