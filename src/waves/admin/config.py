""" WAVES application configuration parameters admin """

from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.admin import register
from waves.models import WavesConfiguration
from django.utils.html import format_html
from waves.forms.admin.site import SiteForm
from django.contrib.sites.models import Site


# TODO add button action for queue (stop / start / restart)
# TODO add action button to invoke command 'dump' for WAVES config

class WavesSiteAdmin(admin.ModelAdmin):
    """ Admin WAVES application parameters """
    list_display = ('domain', 'name', 'theme', 'current_queue_state')
    fieldsets = [
        ('Site', {
            'classes': ('suit-tab', 'suit-tab-general',),
            'fields': ['domain', 'name']
        }),
        ('Frontend configuration', {
            'fields': ['theme',
                       'allow_registration',
                       'allow_submits',
                       'maintenance']
        }),
        ('Queue', {
            'fields': ['current_queue_state']

        })

    ]
    readonly_fields = ('current_queue_state',)
    form = SiteForm

    class Media:
        css = {
            'screen': ('waves/css/site.css',)
        }

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


admin.site.unregister(Site)
admin.site.register(WavesConfiguration, WavesSiteAdmin)
