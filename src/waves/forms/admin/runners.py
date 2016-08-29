from __future__ import unicode_literals

from django.forms import ModelForm, Textarea, Select, TextInput, CheckboxInput, BooleanField, ChoiceField
from django.utils.module_loading import import_string

from waves.models import Runner, RunnerParam


__all__ = ['RunnerForm', 'RunnerParamForm']


def get_runners_list():
    from waves.runners import get_implementation
    classes_list = [('', 'Select a implementation class...')]
    for class_name in get_implementation():
        clazz = import_string(class_name)
        classes_list.append((class_name, class_name))
    return classes_list


class RunnerForm(ModelForm):
    update_init_params = BooleanField(required=False, help_text='Update from clazz')

    class Meta:
        model = Runner
        exclude = ['id']
        widgets = {
            'description': Textarea(attrs={'rows': 5}),
            'clazz': Select(choices=get_runners_list()),
            'available': CheckboxInput(),
            'update_init_params': CheckboxInput()
        }

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


