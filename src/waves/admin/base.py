from __future__ import unicode_literals

from django.conf import settings
from django.contrib import admin

if 'tabbed_admin' in settings.INSTALLED_APPS:
    from tabbed_admin import TabbedModelAdmin
    print 'tabbed model admin'
    class WavesTabbedModelAdmin(TabbedModelAdmin):
        class Media:
            css = {
                'all': ('tabbed_admin/css/tabbed_admin.css',)
            }
            admin_template = 'tabbed_change_form.html'

else:
    print "Classic model admin"
    class WavesTabbedModelAdmin(admin.ModelAdmin):
        class Media:
            admin_template = 'change_form.html'
