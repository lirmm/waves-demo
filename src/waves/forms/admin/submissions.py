from django import forms
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError, ObjectDoesNotExist
from django.forms import ModelForm, Textarea

from waves.models.submissions import ServiceSubmission, ServiceInput, RelatedInput, ServiceInputSample, ServiceOutput


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