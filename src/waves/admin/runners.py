from __future__ import unicode_literals

from django.contrib import admin
from django.contrib import messages
from django.contrib.admin import TabularInline

import waves.const
from waves.forms.admin import RunnerParamForm, RunnerForm
from waves.models import RunnerParam, Runner


class RunnerParamInline(TabularInline):
    """
    Job Runner class instantiation parameters insertion field
    """
    model = RunnerParam
    form = RunnerParamForm
    extra = 0
    fields = ['name', 'default']
    readonly_fields = ('name',)

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


class RunnerAdmin(admin.ModelAdmin):
    model = Runner
    form = RunnerForm
    inlines = (
        RunnerParamInline,
    )

    # fields = ('name', 'description', 'available', 'clazz')
    list_display = ('name', 'impl_clazz', 'available', 'short_description')
    list_filter = ('name', 'available')
    fieldsets = [
        ('General', {
            'fields': ['name', 'available', 'clazz', 'description', 'update_init_params']
        }
         ),
    ]

    def impl_clazz(self, obj):
        return obj.clazz

    impl_clazz.short_description = 'Adaptor class'

    def save_model(self, request, obj, form, change):
        super(RunnerAdmin, self).save_model(request, obj, form, change)
        if obj is not None and ('update_init_params' in form.changed_data or 'clazz' in form.changed_data):
            if 'update_init_params' in form.changed_data:
                print "update init params"
            obj.runner_params.all().delete()
            params = []
            for name, initial in obj.adaptor.init_params.items():
                params.append(RunnerParam(default=initial, name=name, runner=obj))
            RunnerParam.objects.bulk_create(params)
            for service in obj.runs.all():
                service.status = waves.const.SRV_TEST
                # force insert new default values
                jobs = service.reset_runner_params(params, erase=('update_init_params' in form.changed_data))
                message = 'Service %s has been disabled, please check configuration' % service.name
                for job in jobs:
                    message += '<br/>- Related unfinished job %s has been cancelled' % job.title
                messages.warning(request, message)
                service.save()

    def get_form(self, request, obj=None, **kwargs):
        return super(RunnerAdmin, self).get_form(request=request, obj=obj, **kwargs)

admin.site.register(Runner, RunnerAdmin)
