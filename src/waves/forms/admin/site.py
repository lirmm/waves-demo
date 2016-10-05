"""
Admin site for WAVES application configuration
.. TODO:
    Transfer waves.env config variables into this admin if possible
"""
from __future__ import unicode_literals

from django.forms import ModelForm
from waves.models import WavesSite
from django import forms


class SiteForm(ModelForm):
    class Meta:
        model = WavesSite
        fields = '__all__'

    current_queue_status = forms.BooleanField(label="Queue status", widget=forms.widgets.HiddenInput)


