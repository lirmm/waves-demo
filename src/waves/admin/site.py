""" WAVES application configuration parameters admin """

from __future__ import unicode_literals

from django.contrib import admin
from waves.models import WavesApplicationConfiguration
from django.utils.html import format_html
from waves.forms.admin.site import SiteForm


# TODO add button action for queue (stop / start / restart)
# TODO add action button to invoke command 'dump' for WAVES config
class WavesSiteAdmin(admin.ModelAdmin):
    """ Admin WAVES application parameters """
    list_display = ('site', 'get_name', 'theme', 'current_queue_state')
    fieldsets = [
        ('Site', {
            'classes': ('suit-tab', 'suit-tab-general',),
            'fields': ['site', ]
        }),
        ('Frontend configuration', {
            'fields': ['theme', 'get_name', ]
        }),
        ('Queue', {
            'fields': ['current_queue_state']

        })

    ]
    readonly_fields = ('get_name', 'current_queue_state',)
    form = SiteForm

    class Media:
        css = {
            'screen': ('waves/css/site.css',)
        }

    def get_name(self, obj):
        return obj.site.name

    get_name.short_description = 'Global name'

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


admin.site.register(WavesApplicationConfiguration, WavesSiteAdmin)
