""" WAVES application configuration parameters admin """

from __future__ import unicode_literals

from django.contrib import admin
from django.utils.html import format_html

from waves.models import WavesSite

__all__ = ['WavesSiteAdmin']

# TODO add button action for queue (stop / start / restart)
# TODO add action button to invoke command 'dump' for WAVES config


@admin.register(WavesSite)
class WavesSiteAdmin(admin.ModelAdmin):
    """ Admin WAVES application parameters """
    list_display = ('domain', 'name', 'theme', 'current_queue_state', 'site')
    fieldsets = [
        ('Site', {
            'classes': ('suit-tab', 'suit-tab-general',),
            'fields': ['site', 'maintenance']
        }),
        ('Frontend configuration', {
            'fields': ['theme',
                       'allow_registration',
                       'allow_submits',
                       ]
        }),
        ('Job queue', {
            'fields': ['current_queue_state']

        })

    ]
    readonly_fields = ('current_queue_state', 'domain', 'name',)

    def current_queue_state(self, obj):
        from waves.management.waves_commands import JobQueueCommand
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

    def config_file_content(self):
        pass

    def domain(self, obj):
        return obj.site.domain

    def name(self, obj):
        return obj.site.name
