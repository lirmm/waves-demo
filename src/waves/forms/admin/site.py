"""
Admin site for WAVES application configuration
.. TODO:
    Transfer waves.env config variables into this admin if possible
"""
from __future__ import unicode_literals

from django.forms import ModelForm
from waves.models import WavesApplicationConfiguration


class SiteForm(ModelForm):
    class Meta:
        model = WavesApplicationConfiguration
        fields = '__all__'

