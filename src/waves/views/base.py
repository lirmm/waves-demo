""" Simple Views for WAVES """
from __future__ import unicode_literals

from django.contrib.sites.shortcuts import get_current_site as current_site
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.views import generic
import waves.settings
from waves.models import WavesSite
__all__ = ['WavesBaseContextMixin', 'HomePage', 'AboutPage', 'HTML403', 'RestServices', 'css_theme']


def css_theme(request):
    """ Define current setup for WAVES bootstrap theme """
    try:
        site = current_site(request)
        wave_site = WavesSite.get(site=site)
        if wave_site:
            current_theme = wave_site.theme
    except (ObjectDoesNotExist, MultipleObjectsReturned, AttributeError):
        # get default from settings
        current_theme = waves.settings.WAVES_BOOTSTRAP_THEME
    return current_theme


class WavesBaseContextMixin(generic.base.ContextMixin):
    """ Uses of css_theme in templates """
    def get_context_data(self, **kwargs):
        context = super(WavesBaseContextMixin, self).get_context_data(**kwargs)
        context['css_theme'] = css_theme(self.request)
        return context


class HomePage(generic.TemplateView, WavesBaseContextMixin):
    """ WAVES home page"""
    template_name = "home.html"


class AboutPage(generic.TemplateView, WavesBaseContextMixin):
    """ WAVES about page """
    template_name = "about.html"


class HTML403(generic.TemplateView, WavesBaseContextMixin):
    """ WAVES 403 page """
    template_name = "403.html"


class RestServices(generic.TemplateView, WavesBaseContextMixin):
    """ REST API service presentation page """
    template_name = "rest/rest_api.html"
