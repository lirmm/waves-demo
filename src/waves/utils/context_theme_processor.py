from __future__ import unicode_literals

from django.contrib.sites.shortcuts import get_current_site as current_site
from waves.models.site import WavesSite


def get_current_site(request):
    """
    Checks if contrib.sites is installed and returns either the current
    ``Site`` object or a ``RequestSite`` object based on the request.
    """
    site = current_site(request)
    return WavesSite.on_site.filter(site=site)[0]


def css_theme(request):
    try:
        current_theme = get_current_site(request).theme
    except AttributeError:
        current_theme = 'flatly'
    return {'BOOTSTRAP_CSS_THEME': current_theme}
