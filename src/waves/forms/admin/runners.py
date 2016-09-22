from __future__ import unicode_literals

from django.forms import ModelForm, Textarea, Select, TextInput, CheckboxInput, BooleanField, ChoiceField
from django.utils.module_loading import import_string

from waves.models import Runner, RunnerParam


__all__ = ['RunnerForm', 'RunnerParamForm']


def get_runners_list():
    from waves.adaptors import get_implementation
    classes_list = [('', 'Select a implementation class...')]
    for class_name in get_implementation():
        clazz = import_string(class_name)
        classes_list.append((class_name, class_name))
    return classes_list


class RunnerForm(ModelForm):
    class Meta:
        model = Runner
        exclude = ['id']
        widgets = {
            'clazz': Select(choices=get_runners_list()),
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


