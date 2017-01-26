from __future__ import unicode_literals

from django.forms import ModelForm, TextInput, ChoiceField, PasswordInput
from waves.models.adaptors import AdaptorInitParam


class AdaptorInitParamForm(ModelForm):
    """
    Runner defaults param form
    """
    class Meta:
        """ Metas """
        model = AdaptorInitParam
        fields = ['name', "value", 'prevent_override']
        widgets = {
            "value": TextInput(attrs={'size': 50})
        }

    def __init__(self, **kwargs):
        super(AdaptorInitParamForm, self).__init__(**kwargs)
        instance = kwargs.get('instance', None)
        if instance:
            try:
                from django.utils.module_loading import import_string
                from ast import literal_eval
                if instance.content_object.adaptor_defaults.get(instance.name):
                    param_defaults = instance.content_object.adaptor_defaults.get(instance.name)
                    default_value = None
                    initial = instance.value if instance.value else default_value
                    if type(param_defaults) == tuple:
                        self.fields['value'] = ChoiceField(choices=param_defaults, initial=initial)
                if instance.crypt:
                    # self.fields['name'] = instance.name.replace('crypt_', '')
                    self.fields['value'].widget = PasswordInput(render_value=instance.value,
                                                                attrs={'autocomplete': 'new-password'})
            except ValueError:
                pass
