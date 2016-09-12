from __future__ import unicode_literals

from django.contrib.sites.shortcuts import get_current_site as current_site
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.views import generic

import waves.settings
from waves.models import WavesSite


def css_theme(request):
    try:
        site = current_site(request)
        wave_site = WavesSite.on_site.get(site=site)
        if wave_site:
            current_theme = wave_site.theme
    except (ObjectDoesNotExist, MultipleObjectsReturned, AttributeError):
        # get default from settings
        current_theme = waves.settings.WAVES_BOOTSTRAP_THEME
    return current_theme


class WavesBaseContextMixin(generic.base.ContextMixin):
    def get_context_data(self, **kwargs):
        context = super(WavesBaseContextMixin, self).get_context_data(**kwargs)
        context['css_theme'] = css_theme(self.request)
        return context


class HomePage(generic.TemplateView, WavesBaseContextMixin):
    template_name = "home.html"


class AboutPage(generic.TemplateView, WavesBaseContextMixin):
    template_name = "about.html"


class HTML403(generic.TemplateView, WavesBaseContextMixin):
    template_name = "403.html"




