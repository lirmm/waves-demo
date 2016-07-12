from __future__ import unicode_literals

import copy

from django import forms
from django.conf import settings
from django.utils.module_loading import import_string

from waves.models import Service, ServiceInput
from waves.utils.validators import ServiceInputValidator
import waves.const


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
        user = kwargs.pop('user')
        # TODO add re- captcha for unauthenticated user
        # https://www.marcofucci.com/blog/integrating-recaptcha-with-django/
        # and https://github.com/praekelt/django-recaptcha
        super(ServiceJobForm, self).__init__(*args, **kwargs)
        self.helper = self.get_helper(form_tag=form_tag)
        # dynamically add fields according to service parameters
        self.list_inputs = instance.service_inputs.filter(relatedinput=None)
        self.helper.init_layout()
        self.fields['title'].initial = '%s job' % instance.name
        for service_input in self.list_inputs:
            self.helper.set_field(service_input, self)
            self.helper.set_layout(service_input)
            # TODO handle copy/paste content field
            for dependent_input in service_input.dependent_inputs.all():
                # conditional parameters must not be required to use classic django form validation process
                dependent_input.required = False
                self.helper.set_field(dependent_input, self)
                self.helper.set_layout(dependent_input)
        self.helper.end_layout()

    def clean(self):
        cleaned_data = super(ServiceJobForm, self).clean()
        # TODO add form field format validation
        validator = ServiceInputValidator()
        for data in self.cleaned_data:
            srv_input = next((x for x in self.list_inputs if x.name == data), None)
            if srv_input:
                print data, ' input ', srv_input, self.cleaned_data[data]
                validator.validate_input(srv_input, self.cleaned_data[data])
        return cleaned_data

    def save(self, commit=True):
        return super(ServiceJobForm, self).save(commit)
