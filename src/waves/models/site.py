from __future__ import unicode_literals

from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager
from django.db import models
from bootstrap_themes import list_themes
import waves.settings


class WavesSite(models.Model):
    """
    Main application configuration entity,
    # TODO add
    """
    class Meta:
        verbose_name = "WAVES configuration"

    site = models.OneToOneField(Site, on_delete=models.CASCADE)
    theme = models.CharField('Bootstrap theme', max_length=255, default=waves.settings.WAVES_BOOTSTRAP_THEME,
                             choices=list_themes(), )
    objects = models.Manager()
    on_site = CurrentSiteManager('site')

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        Site.objects.clear_cache()
        super(WavesSite, self).save(force_insert, force_update, using, update_fields)

