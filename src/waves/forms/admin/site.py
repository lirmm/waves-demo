"""
Admin site for WAVES application configuration
.. TODO:
    Transfer waves.env config variables into this admin if possible
"""
from __future__ import unicode_literals

from django.forms import ModelForm
from waves.models import WavesSite


class SiteForm(ModelForm):
    class Meta:
        model = WavesSite
        fields = '__all__'

