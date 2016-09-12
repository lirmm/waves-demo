from __future__ import unicode_literals

from django import forms
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.forms import ModelForm, Textarea
from django.core import validators
from crispy_forms.layout import Layout, Div, Field, Button
from crispy_forms.helper import FormHelper
from django.core.exceptions import NON_FIELD_ERRORS
from waves.commands import get_commands_impl_list
from waves.models.services import *
from waves.models.samples import ServiceInputSample
import waves.const as const
import waves.settings

__all__ = ['ServiceForm', 'ServiceCategoryForm', 'ImportForm', 'ServiceSubmissionForm', 'RelatedInputForm',
           'ServiceInputSampleForm', 'ServiceMetaForm', 'ServiceRunnerParamForm', 'ServiceOutputForm',
           'ServiceInputForm', 'ServiceOutputFromInputSubmissionForm']


class ServiceOutputFromInputSubmissionForm(ModelForm):
    class Meta:
        model = ServiceOutputFromInputSubmission
        fields = '__all__'

    # srv_input = AutoCompleteSelectField('related_input', required=True, help_text="Select related submission input")
    def clean(self):
        return super(ServiceOutputFromInputSubmissionForm, self).clean()


class ServiceSubmissionForm(ModelForm):
    class Meta:
        model = ServiceSubmission
        fields = '__all__'
        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': "Only one submission as 'default' for service",
            }
        }


class ImportForm(forms.Form):

    tool_list = forms.ChoiceField(required=True, widget=forms.Select(attrs={'size': '10'}))

    def __init__(self, *args, **kwargs):
        tool_list = kwargs.pop('tool_list', ())
        super(ImportForm, self).__init__(*args, **kwargs)
        self.fields['tool_list'].choices = tool_list
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.render_unmentioned_fields = True
        self.helper.form_show_labels = True
        self.helper.form_show_errors = True
        self.helper.layout = Layout(
            Field('tool_list'),
        )
        if len(self.fields['tool_list'].choices) != 0:
            self.helper.layout.extend(
                Div(
                    Button('launch-import', 'Launch Import',
                           css_id='launch-import',
                           css_class="btn btn-high btn-info grp-button text-center", ),
                    style='text-align:center; padding-top:5px'
                )
            )
        else:
            self.helper.layout.extend(
                Div(
                    Button('launch-import', 'Launch Import',
                           css_id='launch-import',
                           css_class="btn btn-high btn-info grp-button text-center",
                           disabled='disabled'),
                    style='text-align:center; padding-top:5px'
                )
            )

    def clean(self):
        cleaned_data = super(ImportForm, self).clean()
        if 'tool_list' not in cleaned_data:
            raise ValidationError('Please select a tool in list')
        return cleaned_data


class ServiceMetaForm(forms.ModelForm):
    """
    A ServiceMeta form part for inline insertion
    """
    class Meta:
        exclude = ['id']
        model = ServiceMeta
        fields = ['type', 'value', 'description', 'order']
    description = forms.CharField(widget=Textarea(attrs={'rows': 3, 'class': 'input-xlarge'}), required=False)

    def clean(self):
        try:
            validator = validators.URLValidator()
            validator(self.cleaned_data['value'])
            self.instance.is_url = True
        except ValidationError as e:
            if self.instance.type in (const.META_WEBSITE, const.META_DOC, const.META_DOWNLOAD):
                raise e
        return super(ServiceMetaForm, self).clean()


class ServiceInputBaseForm(forms.ModelForm):
    class Meta:
        fields = ['label', 'param_type', 'name', 'type', 'display', 'editable', 'format', 'default', 'description',
                  'multiple']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'span8'}),
            'label': forms.TextInput(attrs={'class': 'span8'}),
            'default': forms.TextInput(attrs={'class': 'span8'}),
            'type': forms.Select(attrs={'class': 'span8'}),
            'format': Textarea(attrs={'rows': 7, 'class': 'span8'}),
        }

    def __init__(self, *args, **kwargs):
        super(ServiceInputBaseForm, self).__init__(*args, **kwargs)
        self.fields['display'].help_text = 'Only used for List Input'


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
        cleaned_data.pop('baseinput_ptr', None)
        return cleaned_data


class RelatedInputForm(ServiceInputBaseForm):
    class Meta(ServiceInputBaseForm.Meta):
        fields = ServiceInputBaseForm.Meta.fields + ['when_value', 'related_to']
        exclude = ['baseinput_ptr']
        model = RelatedInput
        widgets = ServiceInputBaseForm.Meta.widgets

    def save(self, commit=True):
        # self.cleaned_data['service_id'] = self.instance.related_to.service.pk
        # self.instance.service = self.instance.related_to.service
        return super(RelatedInputForm, self).save(commit)

    def __init__(self, *args, **kwargs):
        super(RelatedInputForm, self).__init__(*args, **kwargs)
        try:
            if self.instance and self.instance.related_to and self.instance.related_to.get_choices():
                self.fields['when_value'] = forms.ChoiceField(choices=self.instance.related_to.get_choices())
        except ObjectDoesNotExist:
            pass

    def clean(self):
        cleaned_data = super(RelatedInputForm, self).clean()
        cleaned_data.pop('baseinput_ptr', None)
        return cleaned_data


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
        fields = ['name', 'from_input', 'description', 'short_description']
        widgets = {
            'description': Textarea(attrs={'rows': 1, 'class': 'input-xlarge'}),
            'short_description': Textarea(attrs={'rows': 1, 'class': 'input-xlarge'}),
        }

    def clean(self):
        cleaned_data = super(ServiceOutputForm, self).clean()
        return cleaned_data
        print self.cleaned_data
        count_related_input = self.instance.from_input_submission.count()
        submission_count = self.instance.service.submissions.count()

        print "comparing ", count_related_input, submission_count
        if self.instance.from_input and count_related_input < submission_count:
            raise ValidationError('If you set a pattern, please configure related input for each submission')
        if 0 < count_related_input < submission_count:
            raise ValidationError(
                'If output is valuated from an input, please configure related input for each submission')



class ServiceForm(forms.ModelForm):
    """
    Service form parameters
    """

    class Meta:
        model = Service
        fields = '__all__'
        widgets = {
            'clazz': forms.Select(choices=get_commands_impl_list()),
        }

    def __init__(self, *args, **kwargs):
        super(ServiceForm, self).__init__(*args, **kwargs)
        self.fields['restricted_client'].label = "Restrict access to specified user"
        if not waves.settings.WAVES_NOTIFY_RESULTS:
            self.fields['email_on'].widget.attrs['readonly'] = True
            self.fields['email_on'].help_text = '<span class="warning">Disabled by main configuration</span><br/>' \
                                                + self.fields['email_on'].help_text

    def clean_email_on(self):
        if not waves.settings.WAVES_NOTIFY_RESULTS:
            return self.instance.email_on
        else:
            return self.cleaned_data.get('email_on')

    def clean(self):
        cleaned_data = super(ServiceForm, self).clean()
        # TODO validate that for each submission setup, each 'valuated from input' output is set up accordingly
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
