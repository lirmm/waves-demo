from __future__ import unicode_literals

from django import forms
from django.conf import settings
from django.forms.models import inlineformset_factory
from django.utils.module_loading import import_string

from waves.models import Service, ServiceInput
from waves.utils.validators import ServiceInputValidator

def popover_html(content):
    return '<a tabindex="0" role="button" data-toggle="popover" data-html="true" \
                            data-trigger="hover" data-placement="auto" data-content="' + content + '"> \
                            <span class="glyphicon glyphicon-info-sign"></span></a>'


class ServiceJobInputInline(forms.ModelForm):
    class Meta:
        model = ServiceInput
        fields = ('name', 'type')

    def __init__(self, *args, **kwargs):
        super(ServiceJobInputInline, self).__init__(*args, **kwargs)
        self.helper = self.get_helper(form_tag=False)
        self.helper.form_tag = False
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-4'
        self.helper.field_class = 'col-lg-8'


class ServiceJobForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['title', 'email']

    title = forms.CharField(label="Name your analysis", required=False)
    email = forms.EmailField(label="Mail me results", required=False)

    @staticmethod
    def get_helper(**kwargs):
        try:
            helper = import_string('.'.join(['waves', 'forms', 'lib', settings.WAVES_FORM_PROCESSOR, 'FormHelper']))
            return helper(**kwargs)
        except ImportError:
            raise None

    def __init__(self, *args, **kwargs):
        instance = kwargs.pop('instance')
        form_tag = kwargs.pop('form_tag', True)
        super(ServiceJobForm, self).__init__(*args, **kwargs)
        self.helper = self.get_helper(form_tag=form_tag)
        # dynamically add fields according to service parameters
        self.list_inputs = instance.service_inputs.filter(relatedinput=None)
        for service_input in self.list_inputs:
            self.fields[service_input.name] = self.helper.get_field_for_type(service_input)
            for dependent_input in service_input.dependent_inputs.all():
                self.fields[dependent_input.name] = self.helper.get_field_for_type(dependent_input)
        self.helper.set_layout(self.list_inputs)

    def clean(self):
        # from waves.utils.validators import validate_input
        cleaned_data = super(ServiceJobForm, self).clean()
        # TODO add form field format validation
        validator = ServiceInputValidator()
        for field in self.fields:
            srv_input = next((x for x in self.list_inputs if x.name == field), None)
            if srv_input:
                print field, ' input ', srv_input, field.__class__
                validator.validate_input(srv_input, cleaned_data[field])
        return cleaned_data

    def save(self, commit=True):
        return super(ServiceJobForm, self).save(commit)

ServiceJobInputFormSet = inlineformset_factory(Service,
                                               ServiceInput,
                                               form=ServiceJobForm,
                                               extra=0,
                                               can_delete=False,
                                               can_order=False)
