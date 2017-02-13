from __future__ import unicode_literals

from django.contrib.sites.shortcuts import get_current_site as current_site
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from waves.models.config import WavesSiteConfig
import waves.settings


def css_theme(request):
    theme = waves.settings.WAVES_BOOTSTRAP_THEME
    try:
        theme = WavesSiteConfig.objects.get_current_config().theme
    except (ObjectDoesNotExist, MultipleObjectsReturned, AttributeError) as e:
        pass
    return {'css_theme': theme}
