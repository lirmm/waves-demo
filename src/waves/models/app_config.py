""" Waves application configuration  """
from __future__ import unicode_literals

from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager
from django.db import models
import waves.settings
from waves.compat import list_themes


class WavesApplicationConfiguration(models.Model):
    """
    Main application configuration entity
    # TODO add
    """
    class Meta:
        verbose_name = "WAVES Application"

    site = models.OneToOneField(Site, on_delete=models.CASCADE)
    theme = models.CharField('Bootstrap theme', max_length=255, default=waves.settings.WAVES_BOOTSTRAP_THEME,
                             choices=list_themes(), )
    objects = models.Manager()
    on_site = CurrentSiteManager('site')

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        """ Clear Site cache upon saving """
        Site.objects.clear_cache()
        super(WavesApplicationConfiguration, self).save(force_insert, force_update, using, update_fields)
