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
            'available': CheckboxInput(),
            'update_init_params': CheckboxInput()
        }

    class Media:
        """ Medias """
        js = ('waves/js/runner.js',)

    update_init_params = BooleanField(required=False, label='Reset associated services to default',
                                      help_text='Reload from selected class implementation')

    def __init__(self, *args, **kwargs):
        super(RunnerForm, self).__init__(*args, **kwargs)
        self.fields['clazz'] = ChoiceField(choices=lazy(get_runners_list, tuple)())

        if self.instance.pk is None:
            # print "creation"
            self.fields['update_init_params'].widget = HiddenInput()
            self.fields['update_init_params'].initial = False
            self.fields['available'].initial = False
        else:
            pass


class RunnerParamForm(ModelForm):
    """
    Runner defaults param form
    """
    class Meta:
        """ Metas """
        model = RunnerParam
        fields = ['name', 'default', 'prevent_override']
        widgets = {
            'name': TextInput(attrs={'readonly': True}),
            'default': TextInput()
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
                    initial = instance.default if instance.default else default_value
                    if type(param_defaults) == tuple:
                        self.fields['default'] = ChoiceField(choices=param_defaults, initial=initial)
                if instance.name.startswith('crypt_'):
                    self.fields['default'].widget = PasswordInput(render_value=instance.default)
            except ValueError:
                pass





