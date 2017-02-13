""" Waves application configuration  """
from __future__ import unicode_literals

from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from bootstrap_themes import list_themes

__all__ = ['WavesSiteConfig']

config_keys = [
    "WAVES_ACCOUNT_ACTIVATION_DAYS",
    "WAVES_BOOTSTRAP_THEME",
    "WAVES_APP_NAME",
    "WAVES_FORM_PROCESSOR",
    "WAVES_APP_VERBOSE_NAME",
    "WAVES_TEMPLATE_PACK",
    "WAVES_SERVICES_EMAIL",
    "WAVES_ADMIN_EMAIL",
    "WAVES_JOB_DIR",
    "WAVES_KEEP_ANONYMOUS_JOBS",
    "WAVES_UPLOAD_MAX_SIZE",
    "WAVES_DATA_ROOT",
    "WAVES_SAMPLE_DIR",
    "WAVES_JOBS_MAX_RETRY",
    "WAVES_LOG_ROOT",
    "WAVES_QUEUE_LOG_LEVEL",
    "WAVES_KEEP_REGISTERED_JOBS",
]


def list_config_keys():
    return config_keys


class WavesSiteConfigManager(models.Manager):
    def get_current_config(self):
        # TODO add contrib.site test to check if multiple site is enabled
        try:
            return self.get(pk=1)
        except ObjectDoesNotExist:
            import warnings
            warnings.warn("Not Waves config available for")
            return WavesSiteConfig(theme='default', allow_registration=False, allow_submits=False, maintenance=False)


class WavesSiteConfig(models.Model):
    """
    Main application configuration entity
    # TODO add
    """

    class Meta:
        db_table = "waves_configuration"
        verbose_name = "Waves config"
        verbose_name_plural = "Waves configuration"

    objects = WavesSiteConfigManager()
    theme = models.CharField('Bootstrap theme', max_length=255, choices=list_themes(), default="default")
    allow_registration = models.BooleanField('Registration', default=True,
                                             help_text="Allow user registration")
    allow_submits = models.BooleanField('Allow job submissions', default=True,
                                        help_text="Globally set if job can be submitted")
    maintenance = models.BooleanField('Site Maintenance', default=False, help_text="Redirect everything to 503")

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        """ Clear Site cache upon saving """
        # Site.objects.clear_cache()
        super(WavesSiteConfig, self).save(force_insert, force_update, using, update_fields)


class WavesConfigVar(models.Model):
    """ Config var view fake model to view settings in BO
    TODO: need clean code """
    class Meta:
        db_table = "waves_config_var"
        verbose_name_plural = "Detailed configuration"
        verbose_name = "Configuration item"
        ordering = ['name']

    config = models.ForeignKey(WavesSiteConfig, related_name="config_vars", on_delete=models.CASCADE)
    name = models.CharField('Var name', max_length=200, null=False, primary_key=True)
    value = models.CharField('Config Value', max_length=255, null=False)
