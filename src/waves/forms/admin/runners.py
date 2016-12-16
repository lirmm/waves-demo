"""
Runner configuration BackOffice Forms
"""
from __future__ import unicode_literals

from django.forms import ModelForm, PasswordInput, TextInput, CheckboxInput, BooleanField, ChoiceField, HiddenInput
from django.utils.functional import lazy

from waves.models import Runner, RunnerParam
from waves.utils.runners import get_runners_list

__all__ = ['RunnerForm', 'RunnerParamForm']


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
        js = ('waves/admin/js/runner.js',
              'waves/admin/js/modal.js')
        css = {
            'screen': ('waves/admin/css/modal.css',),
        }

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


class RunnerParamForm(ModelForm):
    """
    Runner defaults param form
    """
    class Meta:
        """ Metas """
        model = RunnerParam
        fields = ['name', "value", 'prevent_override']
        widgets = {
            "value": TextInput(attrs={'size': 50})
        }

    def __init__(self, **kwargs):
        super(RunnerParamForm, self).__init__(**kwargs)
        instance = kwargs.get('instance', None)
        if instance:
            try:
                from django.utils.module_loading import import_string
                Adaptor = import_string(instance.runner.clazz)
                adaptor_default = Adaptor()
                from ast import literal_eval
                if adaptor_default.init_params.get(instance.name):
                    param_defaults = adaptor_default.init_params.get(instance.name)
                    default_value = None
                    initial = instance.value if instance.value else default_value
                    if type(param_defaults) == tuple:
                        self.fields['value'] = ChoiceField(choices=param_defaults, initial=initial)
                if instance.name.startswith('crypt_'):
                    self.fields['value'].widget = PasswordInput(render_value=instance.value)
            except ValueError:
                pass
