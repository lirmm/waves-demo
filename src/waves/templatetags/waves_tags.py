from __future__ import unicode_literals

from django import template
import waves.settings

register = template.Library()


# ADMIN_TITLE
@register.simple_tag
def get_admin_title():
    """
    Returns the Title for the Admin-Interface.
    """
    return waves.settings.WAVES_ADMIN_TITLE


@register.simple_tag
def get_app_verbose_name():
    return waves.settings.WAVES_APP_VERBOSE_NAME


@register.simple_tag
def get_app_name():
    return waves.settings.WAVES_APP_NAME

