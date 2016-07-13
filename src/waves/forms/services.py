from __future__ import unicode_literals

import copy

from django import forms
from django.conf import settings
from django.utils.module_loading import import_string
from django.core.exceptions import ValidationError

from waves.models import Service
from waves.utils.validators import ServiceInputValidator
import waves.const


# TODO refactoring for the copy_paste field associated with FileInput (override formfield template ?)
class ServiceJobForm(forms.ModelForm):
    """
    Service Job Submission form
    Allows to create a new job from a service instance
    """
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
            raise RuntimeError('No helper defined for WAVES, unable to create any form')

    def _create_copy_paste_field(self, service_input):
        service_input.mandatory = False # Field is validated in clean process
        cp_service = copy.copy(service_input)
        cp_service.label = 'Or Copy/paste your content'
        cp_service.description = ''
        cp_service.mandatory = False
        cp_service.type = waves.const.TYPE_TEXT
        cp_service.name = 'cp_' + service_input.name
        self.helper.set_field(cp_service, self)
        self.fields[cp_service.name].widget = forms.Textarea(attrs={'cols': 20, 'rows': 10})
        return cp_service

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
        self.list_inputs = list(instance.service_inputs.filter(relatedinput=None))
        self.helper.init_layout()
        self.fields['title'].initial = '%s job' % instance.name
        extra_fields = []
        for service_input in self.list_inputs:
            if service_input.type == waves.const.TYPE_FILE and not service_input.multiple:
                extra_fields.append(self._create_copy_paste_field(service_input))
            self.helper.set_field(service_input, self)
            self.helper.set_layout(service_input, self)
            for dependent_input in service_input.dependent_inputs.all():
                # conditional parameters must not be required to use classic django form validation process
                dependent_input.required = False
                if dependent_input.type == waves.const.TYPE_FILE and not dependent_input.multiple:
                    extra_fields.append(self._create_copy_paste_field(dependent_input))
                self.helper.set_field(dependent_input, self)
                self.helper.set_layout(dependent_input, self)
                # extra_fields.append(dependent_input)
        self.list_inputs.extend(extra_fields)
        self.helper.end_layout()

    def clean(self):
        cleaned_data = super(ServiceJobForm, self).clean()
        validator = ServiceInputValidator()
        for data in copy.copy(cleaned_data):
            # test if a value has been posted
            srv_input = next((x for x in self.list_inputs if x.name == data), None)
            if srv_input:
                posted_data = cleaned_data.get(srv_input.name)
                if srv_input.type == waves.const.TYPE_FILE and not posted_data:
                    # print srv_input.name, srv_input.type
                    if not cleaned_data.get('cp_' + srv_input.name):
                        self.add_error(srv_input.name, ValidationError('You must provide data for %s' % srv_input.label))
                    else:
                        # replace cleaned data for initial field
                        cleaned_data[srv_input.name] = cleaned_data.get('cp_' + srv_input.name)
                else:
                    # print "No ==> ", srv_input.name, srv_input.type
                    validator.validate_input(srv_input, posted_data, self)
        return cleaned_data

    def save(self, commit=True):
        return super(ServiceJobForm, self).save(commit)
