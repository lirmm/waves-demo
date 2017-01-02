from __future__ import unicode_literals

from django import forms
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError, ObjectDoesNotExist
from django.forms import ModelForm, Textarea
import waves.const
from waves.models.submissions import *


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



class SubmissionDataForm(forms.ModelForm):
    """ Base Class for submission forms """
    class Meta:
        widgets = {
            'list_elements': Textarea(attrs={'rows': 3}),
            'short_description': Textarea(attrs={'rows': 4}),
        }


class ParamForm(SubmissionDataForm):
    """ A SubmissionParam form part for inline insertion """

    class Meta(SubmissionDataForm.Meta):
        model = SubmissionParam
        fields = '__all__'

    def clean(self):
        cleaned_data = super(ParamForm, self).clean()
        if self.instance.submitted is False and not cleaned_data.get('default', False):
            raise ValidationError('Non editable fields must have a default value')
        cleaned_data.pop('baseinput_ptr', None)
        return cleaned_data

    def __init__(self, *args, **kwargs):
        super(ParamForm, self).__init__(*args, **kwargs)
        choices = waves.const.IN_TYPE[1:]
        choices.insert(0, ('', '----'))
        self.fields['type'] = forms.ChoiceField(choices=choices)


class FileInputForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        widgets = {
            '_type_format': Textarea(attrs={'rows': 3})
        }

    def __init__(self, *args, **kwargs):
        super(FileInputForm, self).__init__(*args, **kwargs)
        self.fields['list_elements'].help_text = "One extension per line"
        self.fields['list_elements'].label = "Authorized extensions"


class RelatedInputForm(SubmissionDataForm):
    class Meta(SubmissionDataForm.Meta):
        fields = '__all__'
        model = RelatedParam
        widgets = SubmissionDataForm.Meta.widgets

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
        model = SubmissionSample
        fields = '__all__'


class ServiceOutputForm(forms.ModelForm):
    """
    A SubmissionOutput form part for inline insertion
    """

    class Meta:
        model = SubmissionOutput
        fields = '__all__'
        widgets = {
            'description': Textarea(attrs={'rows': 1, 'class': 'input-xlarge'}),
            'short_description': Textarea(attrs={'rows': 1, 'class': 'input-xlarge'}),
        }

    def clean(self):
        cleaned_data = super(ServiceOutputForm, self).clean()
        return cleaned_data
