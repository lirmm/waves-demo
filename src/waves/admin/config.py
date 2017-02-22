""" WAVES application configuration parameters admin """

from __future__ import unicode_literals

from django.contrib import admin
from django.utils.html import format_html

from waves.admin.base import WavesModelAdmin
from waves.admin.forms.config import WavesConfigVarForm, WavesConfigVarFormSet
from waves.models.config import WavesSiteConfig, WavesConfigVar, list_config_keys

__all__ = ['WavesSiteAdmin']

# TODO add button action for queue (stop / start / restart)
# TODO add action button to invoke command 'dump' for WAVES config


class WavesConfigVarInline(admin.TabularInline):
    model = WavesConfigVar
    formset = WavesConfigVarFormSet
    form = WavesConfigVarForm
    extra = 0

    def has_add_permission(self, request):
        return False

    def get_max_num(self, request, obj=None, **kwargs):
        return len(list_config_keys())

    def get_min_num(self, request, obj=None, **kwargs):
        return len(list_config_keys())

    def has_delete_permission(self, request, obj=None):
        return False

    def get_extra(self, request, obj=None, **kwargs):
        return 0


@admin.register(WavesSiteConfig)
class WavesSiteAdmin(WavesModelAdmin):
    """ Admin WAVES application parameters """
    class Media:
        js = (
            'waves/js/bootstrap-switch.min.js',
        )
        css = {
            'all': ('waves/css/bootstrap-switch.min.css',)
        }
    inlines = (WavesConfigVarInline, )
    actions = []
    list_display = ('theme', 'allow_registration', 'allow_submits', 'current_queue_state')
    fieldsets = [
        ('Frontend configuration', {
            'classes': ('suit-tab', 'suit-tab-general',),
            'fields': ['theme',
                       'allow_registration',
                       'allow_submits',
                       'maintenance',
                       ]
        }),
        ('Job queue', {
            'fields': ['current_queue_state']

        })

    ]
    readonly_fields = ('current_queue_state',)

    def get_actions(self, request):
        # Disable delete
        actions = super(WavesSiteAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def current_queue_state(self, obj):
        from waves.management.daemon.command import JobQueueCommand
        from waves.management.daemon.runner import DaemonRunner
        import sys
        sys.argv[0] = 'wavesqueue'
        sys.argv[1] = 'status'
        daemon = DaemonRunner(JobQueueCommand, verbose=False)
        daemon_status = daemon._status()
        if daemon_status == DaemonRunner.STATUS_RUNNING:
            css_class = "led-green"
        elif daemon_status == DaemonRunner.STATUS_STOPPED:
            css_class = "led-red"
        else:
            css_class = "led-yellow"
        return format_html('<div class="led-box"><div class="{}"></div></div>' + daemon_status, css_class)

    def has_add_permission(self, request):
        return False if self.model.objects.count() == 1 else super(WavesSiteAdmin, self).has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser is True
