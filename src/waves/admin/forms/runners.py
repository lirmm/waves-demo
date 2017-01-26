"""
Runner configuration BackOffice Forms
"""
from __future__ import unicode_literals

from django.forms import ModelForm, CheckboxInput, BooleanField, ChoiceField, HiddenInput
from django.utils.functional import lazy

from waves.models import Runner
from waves.utils.runners import get_runners_list

__all__ = ['RunnerForm']


class RunnerForm(ModelForm):
    """ Form to edit a runner
    """
    class Meta:
        """ Metas """
        model = Runner
        exclude = ['id']
        widgets = {
            'update_init_params': CheckboxInput()
        }

    class Media:
        """ Medias """
        js = ('waves/admin/js/runner.js',)

    update_init_params = BooleanField(required=False, label='Reset related services')

    def __init__(self, *args, **kwargs):
        super(RunnerForm, self).__init__(*args, **kwargs)
        self.fields['clazz'] = ChoiceField(label="Run on", choices=lazy(get_runners_list, tuple)())
        if self.instance.pk is None:
            # print "creation"
            self.fields['update_init_params'].widget = HiddenInput()
            self.fields['update_init_params'].initial = False
        else:
            pass
