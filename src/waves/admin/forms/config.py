"""
WAVES configuration BackOffice Forms
"""
from __future__ import unicode_literals

from django import forms
from waves.models.config import WavesConfigVar, list_config_keys
from waves.settings import init_setting


class WavesConfigVarForm(forms.ModelForm):
    class Meta:
        model = WavesConfigVar
        fields = '__all__'
        widgets = {
            'name': forms.widgets.TextInput(attrs={'style': 'width:100%', 'readonly': 'readonly'}),
            'value': forms.widgets.TextInput(attrs={'style': 'width:100%', 'readonly': 'readonly'}),
        }

    def has_changed(self):
        return True


class WavesConfigVarFormSet(forms.models.BaseInlineFormSet):
    model = WavesConfigVar

    def __init__(self, *args, **kwargs):
        super(WavesConfigVarFormSet, self).__init__(*args, **kwargs)
        initial = []
        for key in sorted(list_config_keys()):
            initial.append({'name': key, 'value': init_setting(key)})
        self.initial = initial
