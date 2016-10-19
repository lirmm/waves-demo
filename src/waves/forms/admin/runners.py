"""
Runner configuration BackOffice Forms
"""
from __future__ import unicode_literals
from django.forms import ModelForm, Textarea, Select, TextInput, CheckboxInput, BooleanField
from waves.models import Runner, RunnerParam
import waves.settings
__all__ = ['RunnerForm', 'RunnerParamForm']


def get_runners_list():
    """
    Retrieve enabled adaptors list from waves settings env file
    :return: a list of Tuple 'value'/'label'
    """
    classes_list = [('', 'Select a implementation class...')]
    for adaptor in waves.settings.WAVES_ADAPTORS:
        classes_list.append((adaptor, adaptor.rsplit('.', 1)[1]))
    return classes_list


class RunnerForm(ModelForm):
    """ Form to edit a runner
    """
    class Meta:
        """ Metas """
        model = Runner
        exclude = ['id']
        widgets = {
            'clazz': Select(choices=get_runners_list()),
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
        if self.instance.pk is None:
            # print "creation"
            self.fields['update_init_params'].widget.attrs['disabled'] = True
        else:
            pass


class RunnerParamForm(ModelForm):
    """
    Runner defaults param form
    """
    class Meta:
        """ Metas """
        model = RunnerParam
        fields = ['name', 'default']
        widgets = {
            'name': TextInput(attrs={'readonly': True}),
            'default': Textarea(attrs={'rows': 2, 'class': 'span12'})
        }


