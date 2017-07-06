from __future__ import unicode_literals

from django import template

register = template.Library()


@register.simple_tag
def get_app_name():
    return "WAVES DEMO APPLICATION"
