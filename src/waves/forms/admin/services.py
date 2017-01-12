"""
WAVES Service models forms
"""
from __future__ import unicode_literals

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field
from django import forms
from django.core import validators
from django.core.exceptions import ValidationError
from django.forms import ModelForm, Textarea, TextInput

import waves.const as const
import waves.settings
from waves.commands import get_commands_impl_list
from waves.models.metas import ServiceMeta
from waves.models.services import *
from waves.models.submissions import SubmissionRunParam

__all__ = ['ServiceForm', 'ServiceCategoryForm', 'ImportForm', 'ServiceMetaForm', 'ServiceRunnerParamForm']


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
            widget=forms.widgets.Select(attrs={'size': '15', 'style': 'width:100%; height: auto;'}))

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
        fields = '__all__'

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


class ServiceForm(forms.ModelForm):
    """
    Service form parameters
    """

    class Meta:
        model = Service
        fields = '__all__'
        widgets = {
            'clazz': forms.Select(choices=get_commands_impl_list()),
            'edam_topics': forms.TextInput(attrs={'size': 50}),
            'edam_operations': forms.TextInput(attrs={'size': 50}),
        }

    def __init__(self, *args, **kwargs):
        super(ServiceForm, self).__init__(*args, **kwargs)
        self.fields['restricted_client'].label = "Restrict access to specified user"
        if not self.fields['created_by'].initial:
            self.fields['created_by'].initial = self.current_user
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
        model = SubmissionRunParam
        fields = '__all__'
        widgets = {
            'value': TextInput(attrs={'size': 50})
        }

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None, initial=None, **kwargs):
        super(ServiceRunnerParamForm, self).__init__(data, files, auto_id, prefix, initial, **kwargs)


class ServiceCategoryForm(ModelForm):
    class Meta:
        model = ServiceCategory
        fields = '__all__'
