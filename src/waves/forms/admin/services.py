"""
WAVES Service models forms
"""
from __future__ import unicode_literals

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field
from django import forms
from django.core import validators
from django.core.exceptions import NON_FIELD_ERRORS
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.forms import ModelForm, Textarea, TextInput

import waves.const as const
import waves.settings
from waves.commands import get_commands_impl_list
from waves.models.samples import ServiceInputSample
from waves.models.services import *
from waves.models.submissions import ServiceSubmission, RelatedInput, ServiceOutput, ServiceInput

__all__ = ['ServiceForm', 'ServiceCategoryForm', 'ImportForm', 'ServiceSubmissionForm', 'RelatedInputForm',
           'ServiceInputSampleForm', 'ServiceMetaForm', 'ServiceRunnerParamForm', 'ServiceOutputForm',
           'ServiceInputForm', 'ServiceSubmissionFormSet']


class ServiceSubmissionForm(ModelForm):
    class Meta:
        model = ServiceSubmission
        exclude = ['id', 'slug']
        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': "Only one submission as 'default' for service",
            }
        }

    def clean(self):
        cleaned_data = self.cleaned_data


class ServiceSubmissionFormSet(forms.models.BaseInlineFormSet):
    def clean(self):
        if len(self.forms) == 0:
            raise ValidationError('Please setup a submission ')
        if self.instance.pk is not None or len(self.forms) > 0:
            nb_api = 0
            nb_web = 0
            for form in self.forms:
                nb_api += 1 if form.cleaned_data.get('available_api') is True else 0
                nb_web += 1 if form.cleaned_data.get('available_online') is True else 0
            if nb_api == 0 and self.data.get('api_on') == 'on':
                raise ValidationError('At least one submission must be available for api if service is')
            if nb_web == 0 and self.data.get('web_on') == 'on':
                raise ValidationError('At least one submission must be available for web if service is')


class ImportForm(forms.Form):
    """
    Service Import Form
    """
    category = forms.ModelChoiceField(label='Import to category',
                                      queryset=ServiceCategory.objects.all())
    tool = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        tool_list = kwargs.pop('tool', ())
        selected = kwargs.pop('selected', None)
        super(ImportForm, self).__init__(*args, **kwargs)
        self.fields['tool'] = forms.ChoiceField(
            choices=tool_list,
            initial=selected,
            disabled=('disabled' if selected is not None else ''),
            widget=forms.widgets.Select(attrs={'size': '10'}))

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.render_unmentioned_fields = False
        self.helper.form_show_labels = True
        self.helper.form_show_errors = True
        self.helper.layout = Layout(
            Field('category'),
            Field('tool'),
        )
        self.helper.disable_csrf = True


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
        self.instance.service = self.instance.related_to.service
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
        fields = ['name', 'input', 'file']


class ServiceOutputForm(forms.ModelForm):
    """
    A ServiceOutput form part for inline insertion
    """

    class Meta:
        model = ServiceOutput
        exclude = ['id']
        fields = ['name', 'related_from_input', 'description', 'short_description']
        widgets = {
            'description': Textarea(attrs={'rows': 1, 'class': 'input-xlarge'}),
            'short_description': Textarea(attrs={'rows': 1, 'class': 'input-xlarge'}),
        }

    def clean(self):
        cleaned_data = super(ServiceOutputForm, self).clean()
        return cleaned_data


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
        if not self.fields['created_by'].initial:
            self.fields['created_by'].initial = self.current_user.profile
        if not waves.settings.WAVES_NOTIFY_RESULTS:
            self.fields['email_on'].widget.attrs['readonly'] = True
            self.fields['email_on'].help_text = '<span class="warning">Disabled by main configuration</span><br/>' \
                                                + self.fields['email_on'].help_text

    def clean_email_on(self):
        if not waves.settings.WAVES_NOTIFY_RESULTS:
            return self.instance.email_on
        else:
            return self.cleaned_data.get('email_on')


class ServiceRunnerParamForm(ModelForm):
    class Meta:
        model = ServiceRunnerParam
        fields = ['param', '_value']
        widgets = {
            '_value': TextInput(attrs={'size': 35})
        }

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None, initial=None, **kwargs):
        super(ServiceRunnerParamForm, self).__init__(data, files, auto_id, prefix, initial, **kwargs)


class ServiceCategoryForm(ModelForm):
    class Meta:
        model = ServiceCategory
        fields = '__all__'
