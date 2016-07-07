from __future__ import unicode_literals

from django.apps import AppConfig


class WavesConfig(AppConfig):
    name = "waves"
    verbose_name = 'Waves apps'

    def ready(self):
        from waves.models import signals
