from __future__ import unicode_literals

from django.conf import settings
from django.contrib import admin

if 'tabbed_admin' in settings.INSTALLED_APPS:
    from tabbed_admin import TabbedModelAdmin


    class WavesTabbedModelAdmin(TabbedModelAdmin):
        class Media:
            css = {
                'screen': ('waves/css/tabbed_admin.css', )
            }
        admin_template = 'tabbed_change_form.html'

        @property
        def media(self):
            """
            Overrides media class to skip first parent media import
            """
            media = super(admin.ModelAdmin, self).media
            return media
else:
    class WavesTabbedModelAdmin(admin.ModelAdmin):
        admin_template = 'change_form.html'
