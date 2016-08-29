from __future__ import unicode_literals

from django import template
from django.conf import settings

register = template.Library()

if 'tabbed_admin' in settings.INSTALLED_APPS:
    from tabbed_admin.templatetags import tabbed_admin_tags as waves_tabbed_admin_tags
else:
    pass
