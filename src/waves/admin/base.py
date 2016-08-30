from __future__ import unicode_literals

from django.conf import settings
from django.contrib import admin

if 'tabbed_admin' in settings.INSTALLED_APPS:
    from tabbed_admin import TabbedModelAdmin


    class WavesTabbedModelAdmin(TabbedModelAdmin):
        class Media:
            css = {
                'all': ('tabbed_admin/css/tabbed_admin.css',)
            }
        admin_template = 'tabbed_change_form.html'


else:
    class WavesTabbedModelAdmin(admin.ModelAdmin):
        admin_template = 'change_form.html'
