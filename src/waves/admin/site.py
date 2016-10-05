from __future__ import unicode_literals

from django.contrib import admin
from waves.models import WavesSite
from django.utils.html import format_html
from waves.forms.admin.site import SiteForm


class WavesSiteAdmin(admin.ModelAdmin):
    list_display = ('site', 'get_name', 'theme', 'current_queue_state')
    # search_fields = ('site__domain', 'site__name')
    # fields = ('theme')
    fieldsets = ()
    readonly_fields = ('get_name', 'current_queue_state')
    form = SiteForm

    class Media:
        css = {
            'screen': ('waves/css/site.css',)
        }

    def get_name(self, obj):
        return obj.site.name

    get_name.short_description = 'Global NAME'

    def current_queue_state(self, obj):
        from waves.management.commands.wavesqueue import Command as WavesQueueCommand
        from waves.management.daemon_runner import DaemonRunner
        daemon = DaemonRunner(WavesQueueCommand, argv=['wavesqueue', 'status'])
        daemon_status = daemon._status()
        if daemon_status == DaemonRunner.STATUS_RUNNING:
            css_class = "led-green"
        elif daemon_status == DaemonRunner.STATUS_STOPPED:
            css_class = "led-red"
        else:
            css_class = "led-yellow"
        return format_html('<div class="led-box"><div class="{}"></div></div>', css_class)

    def config_file_content(self):
        pass

    def has_add_permission(self, request):
        return False


admin.site.register(WavesSite, WavesSiteAdmin)
