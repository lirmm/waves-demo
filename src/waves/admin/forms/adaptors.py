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

    def __init__(self, **kwargs):
        super(AdaptorInitParamForm, self).__init__(**kwargs)
        instance = kwargs.get('instance', None)
        if instance:
            try:
                from django.utils.module_loading import import_string
                from ast import literal_eval
                concrete = instance.content_object.get_concrete_adaptor()
                if concrete is not None :
                    default_value = None
                    initial = instance.value if instance.value else default_value
                    choices = getattr(concrete, instance.name + '_choices', None)
                    if choices:
                        self.fields['value'] = ChoiceField(choices=choices, initial=initial)
                if instance.crypt:
                    self.fields['value'].widget = PasswordInput(render_value=instance.value,
                                                                attrs={'autocomplete': 'new-password'})
            except ValueError:
                pass
