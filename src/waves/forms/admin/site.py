"""
Admin site for WAVES application configuration
.. TODO:
    Transfer waves.env config variables into this admin if possible
"""
from __future__ import unicode_literals

from django.forms import ModelForm
from waves.models import WavesConfiguration


class SiteForm(ModelForm):
    class Meta:
        model = WavesConfiguration
        fields = '__all__'

