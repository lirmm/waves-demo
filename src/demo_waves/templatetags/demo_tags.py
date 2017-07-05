from __future__ import unicode_literals

from django import template

import waves.settings
from waves.models import ServiceCategory

register = template.Library()


@register.simple_tag
def get_app_name():
    return "WAVES DEMO APPLICATION"
