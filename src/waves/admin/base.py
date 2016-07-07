from __future__ import unicode_literals

from django.contrib import admin


class TinyMCEAdmin(admin.ModelAdmin):
    class Media:
        js = [
            '/static/grappelli/tinymce/jscripts/tiny_mce/tiny_mce.js',
            '/static/waves/js/tinymce.js',
        ]
