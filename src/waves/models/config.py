""" Waves application configuration  """
from __future__ import unicode_literals

from django.contrib.sites.models import Site
from django.db import models
import waves.settings
from bootstrap_themes import list_themes
__all__ = ['WavesConfiguration']


class WavesConfiguration(Site):
    """
    Main application configuration entity
    # TODO add
    """
    class Meta:
        db_table = "waves_configuration"
        verbose_name = "Application config"

    theme = models.CharField('Bootstrap theme', max_length=255, default=waves.settings.WAVES_BOOTSTRAP_THEME,
                             choices=list_themes(), )
    allow_registration = models.BooleanField('Allow registration', default=True)
    allow_submits = models.BooleanField('Allow job submissions', default=True)
    maintenance = models.BooleanField('Maintenance flag', default=False, help_text="If checked, all user actions"
                                                                                   " redirect to maintenance")
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        """ Clear Site cache upon saving """
        Site.objects.clear_cache()
        super(WavesConfiguration, self).save(force_insert, force_update, using, update_fields)
