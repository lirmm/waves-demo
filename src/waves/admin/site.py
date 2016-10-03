from __future__ import unicode_literals

from django.contrib import admin
from waves.models import WavesSite
from waves.forms.admin.site import SiteForm


class WavesSiteAdmin(admin.ModelAdmin):
    list_display = ('get_domain', 'get_name', 'theme', 'current_queue_state')
    # search_fields = ('site__domain', 'site__name')
    # fields = ('theme')
    form = SiteForm

    class Media:
        css = {
            'screen': ('waves/css/site.css',)
        }

    def get_domain(self, obj):
        return obj.site.domain

    def get_name(self, obj):
        return obj.site.name

    def current_queue_state(self, obj):
        from waves.management.commands.wavesqueue import Command as WavesQueueCommand
        from waves.management.daemon_runner import DaemonRunner
        daemon = DaemonRunner(WavesQueueCommand, argv=['wavesqueue', 'status'])
        return "%s" % daemon._status()

    def config_file_content(self):
        pass

    def has_add_permission(self, request):
        return False

admin.site.register(WavesSite, WavesSiteAdmin)
