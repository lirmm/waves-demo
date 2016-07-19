from __future__ import unicode_literals
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.forms import ModelForm, Textarea
from django.core.exceptions import ValidationError
from crispy_forms.layout import Layout, Div, Field, Button
from crispy_forms.helper import FormHelper

from waves.commands import get_commands_impl_list
from waves.models import ServiceMeta, ServiceInput, RelatedInput, ServiceOutput, \
    ServiceCategory, Service, ServiceRunnerParam, ServiceInputSample
import waves.const as const

__all__ = ['ServiceForm', 'ServiceCategoryForm', 'ImportForm']


class ImportForm(forms.Form):
    tool_list = forms.ChoiceField(required=True, widget=forms.Select(attrs={'size': '10'}), choices=())
    update = forms.BooleanField(label='Update existing',
                                required=False,
                                initial=False)

    def __init__(self, *args, **kwargs):
        try:
            tool_list = kwargs.pop('tool_list')
        except KeyError:
            tool_list = ()
            pass
        super(ImportForm, self).__init__(*args, **kwargs)
        self.fields['tool_list'] = forms.ChoiceField(required=True, choices=tool_list, widget=forms.Select(attrs={'size': '10'}))

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.render_unmentioned_fields = False
        self.helper.form_show_labels = True
        if len(self.fields['tool_list'].choices) != 0:
            self.helper.layout = Layout(
                Field('tool_list'),
                Field('update'),
                Div(
                    Button('launch-import', 'Launch Import',
                           css_id='launch-import',
                           css_class="btn btn-high btn-info grp-button text-center", ),
                    style='text-align:center; padding-top:5px'
                )
            )

    def clean_tool_list(self):
        pass

    def clean(self):
        cleaned_data = super(ImportForm, self).clean()
        if 'tool_list' not in cleaned_data:
            raise ValidationError('Please select a tool')
        return cleaned_data


class ServiceMetaForm(forms.ModelForm):
    """
    A ServiceMeta form part for inline insertion
    """

    class Meta:
        exclude = ['id']
        model = ServiceMeta
        fields = ['type', 'value', 'description', 'order']
        widgets = {
            'description': Textarea(attrs={'rows': 3, 'class': 'input-xlarge'}),
        }


class ServiceInputBaseForm(forms.ModelForm):
    class Meta:
        fields = ['label', 'param_type', 'name', 'type', 'editable', 'format', 'default', 'description',
                  'display', 'multiple']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'span8'}),
            'label': forms.TextInput(attrs={'class': 'span8'}),
            'default': forms.TextInput(attrs={'class': 'span8'}),
            'type': forms.Select(attrs={'class': 'span8'}),
            'format': Textarea(attrs={'rows': 7, 'class': 'span8'}),
            'description': Textarea(attrs={'rows': '2', 'class': 'span8'}),
        }

    def __init__(self, *args, **kwargs):
        super(ServiceInputBaseForm, self).__init__(*args, **kwargs)
        if not self.instance.type == const.TYPE_LIST:
            self.fields['display'].widget = forms.HiddenInput()
        if self.instance.type == const.TYPE_LIST:
            self.fields['default'].widget = forms.Select(choices=self.instance.get_choices())


class ServiceInputForm(ServiceInputBaseForm):
    """
    A ServiceInput form part for inline insertion
    """

    class Meta(ServiceInputBaseForm.Meta):
        fields = ServiceInputBaseForm.Meta.fields + ['order', 'mandatory']
        model = ServiceInput
        widgets = ServiceInputBaseForm.Meta.widgets

    def clean(self):
        cleaned_data = super(ServiceInputForm, self).clean()
        if self.instance.editable is False and not cleaned_data.get('default', False):
            raise ValidationError('Non editable fields must have a default value')
        return cleaned_data


class RelatedInputForm(ServiceInputBaseForm):
    class Meta(ServiceInputBaseForm.Meta):
        fields = ServiceInputBaseForm.Meta.fields + ['when_value']
        model = RelatedInput
        widgets = ServiceInputBaseForm.Meta.widgets

    def save(self, commit=True):
        self.cleaned_data['service_id'] = self.instance.related_to.service.pk
        self.instance.service = self.instance.related_to.service
        return super(RelatedInputForm, self).save(commit)

    def __init__(self, *args, **kwargs):
        super(RelatedInputForm, self).__init__(*args, **kwargs)
        try:
            if self.instance and self.instance.related_to and self.instance.related_to.get_choices():
                self.fields['when_value'] = forms.ChoiceField(choices=self.instance.related_to.get_choices())
        except ObjectDoesNotExist:
            pass


class ServiceInputSampleForm(forms.ModelForm):
    class Meta:
        model = ServiceInputSample
        fields = ['name', 'input', 'file', 'dependent_input', 'when_value']


class ServiceOutputForm(forms.ModelForm):
    """
    A ServiceOutput form part for inline insertion
    """

    class Meta:
        model = ServiceOutput
        exclude = ['id']
        fields = ['name', 'from_input', 'description']
        widgets = {
            'description': Textarea(attrs={'rows': 1, 'class': 'input-xlarge'}),
        }


class ServiceForm(forms.ModelForm):
    """
    Service form parameters
    """

    class Meta:
        model = Service
        fields = ('name', 'api_name', 'version', 'run_on', 'runner_params', 'status', 'description')
        widgets = {
            # 'description': RedactorWidget(editor_options={'lang': 'en', 'maxWidth': '500', 'minHeight': '100'}),
            'clazz': forms.Select(choices=get_commands_impl_list()),
        }

    def __init__(self, *args, **kwargs):
        super(ServiceForm, self).__init__(*args, **kwargs)
        self.fields['restricted_client'].label = "Restrict access to specified user"


    def clean(self):
        # TODO add check if running jobs are currently running, to disable any modification of runner / inputs / outputs
        cleaned_data = super(ServiceForm, self).clean()
        return cleaned_data


class ServiceRunnerParamForm(ModelForm):
    class Meta:
        model = ServiceRunnerParam
        fields = ['param', 'value']
        widgets = {
            'value': Textarea(attrs={'rows': 2, 'class': 'span12'})
        }

    def clean(self):
        cleaned_data = super(ServiceRunnerParamForm, self).clean()
        if not cleaned_data['value'] and self.instance.param.default is None:
            raise ValidationError('%s field need a value !' % self.instance.param.name)
        return cleaned_data


class ServiceCategoryForm(ModelForm):
    class Meta:
        model = ServiceCategory
        fields = ['name', 'parent', 'api_name', 'short_description', 'description', 'ref']
