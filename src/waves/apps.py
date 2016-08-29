from __future__ import unicode_literals
from django.apps import AppConfig


class WavesApp(AppConfig):
    name = "waves"
    verbose_name = 'Web Application for Versatile Evolutionary Services'

    def ready(self):
        from waves.models import signals
