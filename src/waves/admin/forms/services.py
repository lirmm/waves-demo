"""
WAVES Service models forms
"""
from __future__ import unicode_literals

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field
from django import forms
import waves.settings
from waves.commands import get_commands_impl_list
from waves.models import BooleanParam, ListParam, FileInput, TextParam
from waves.models.services import *

__all__ = ['ServiceForm', 'ImportForm', 'ServiceMetaForm']


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


class SampleDepForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SampleDepForm, self).__init__(*args, **kwargs)
        self.fields['related_to'].widget.can_delete_related = False
        self.fields['related_to'].widget.can_add_related = False
        self.fields['related_to'].widget.can_change_related = False


class InputInlineForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(InputInlineForm, self).__init__(*args, **kwargs)
        if isinstance(self.instance, BooleanParam) or isinstance(self.instance, ListParam):
            self.fields['default'] = forms.ChoiceField(choices=self.instance.choices)
            self.fields['default'].required = False
        elif isinstance(self.instance, FileInput):
            self.fields['default'].widget.attrs['disabled'] = True


class TextParamForm(forms.ModelForm):
    class Meta:
        model = TextParam
        exclude = ['order']

    def save(self, commit=True):
        self.instance.__class__ = TextParam
        return super(TextParamForm, self).save(commit)


class InputSampleForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(InputSampleForm, self).__init__(*args, **kwargs)
        self.fields['file_input'].widget.can_delete_related = False
        self.fields['file_input'].widget.can_add_related = False
        self.fields['file_input'].widget.can_change_related = False