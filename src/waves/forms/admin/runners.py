"""
Runner configuration BackOffice Forms
"""
from __future__ import unicode_literals

from django.forms import ModelForm, Textarea, TextInput, CheckboxInput, BooleanField
from waves.models import Runner, RunnerParam


__all__ = ['RunnerForm', 'RunnerParamForm']


class RunnerForm(ModelForm):
    class Meta:
        model = Runner
        exclude = ['id']
        widgets = {
            'available': CheckboxInput(),
            'update_init_params': CheckboxInput()
        }

    class Media:
        js = ('waves/js/runner.js',)

    update_init_params = BooleanField(required=False, label='Reset associated services to default',
                                      help_text='Reload from selected class implementation')

    def __init__(self, *args, **kwargs):
        super(RunnerForm, self).__init__(*args, **kwargs)
        if self.instance.pk is None:
            # print "creation"
            self.fields['update_init_params'].widget.attrs['disabled'] = True
        else:
            # print "update", self.instance
            pass

    def clean(self):
        return super(RunnerForm, self).clean()


class RunnerParamForm(ModelForm):
    class Meta:
        model = RunnerParam
        fields = ['name', 'default']
        widgets = {
            'name': TextInput(attrs={'readonly': True}),
            'default': Textarea(attrs={'rows': 2, 'class': 'span12'})
        }


