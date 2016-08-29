from __future__ import unicode_literals

from django.contrib import admin
from waves.models.site import WavesSite


class TinyMCEAdmin(admin.ModelAdmin):
    class Media:
        pass


class WavesSiteAdmin(admin.ModelAdmin):
    list_display = ('get_domain', 'get_name', 'theme')
    search_fields = ('site__domain', 'site__name')
    fields = ('site', 'theme')

    def get_domain(self, obj):
        return obj.site.domain

    def get_name(self, obj):
        return obj.site.name

    def config_file_content(self):
        pass

admin.site.register(WavesSite, WavesSiteAdmin)
