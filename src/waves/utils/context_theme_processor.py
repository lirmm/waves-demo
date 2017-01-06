from __future__ import unicode_literals

from django.contrib.sites.shortcuts import get_current_site as current_site
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from waves.models.app_config import WavesApplicationConfiguration
import waves.settings


def css_theme(request):
    try:
        site = current_site(request)
        wave_site = WavesApplicationConfiguration.on_site.get(site=site)
        if wave_site:
            current_theme = wave_site.theme
    except (ObjectDoesNotExist, MultipleObjectsReturned, AttributeError):
        # get default from settings
        current_theme = waves.settings.WAVES_BOOTSTRAP_THEME
    return {'css_theme': current_theme}
