from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.sites.admin import Site, SiteAdmin

from waves.models.site import WavesSite


class TinyMCEAdmin(admin.ModelAdmin):
    class Media:
        js = [
            '/static/grappelli/tinymce/jscripts/tiny_mce/tiny_mce.js',
            '/static/waves/js/tinymce.js',
        ]


class WavesSiteAdmin(admin.ModelAdmin):
    list_display = ('get_domain', 'get_name', 'theme')
    search_fields = ('site__domain', 'site__name')
    fields = ('site', 'theme', 'config_file', 'config_file_content')
    readonly_fields = ('config_file', )

    def get_domain(self, obj):
        return obj.site.domain

    def get_name(self, obj):
        return obj.site.name

    def config_file_content(self):
        pass

admin.site.register(WavesSite, WavesSiteAdmin)
