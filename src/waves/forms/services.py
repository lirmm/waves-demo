from __future__ import unicode_literals
import copy
from django import forms
from django.utils.module_loading import import_string
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db.models import Q

from waves.models import Service, ServiceInput
from waves.models.submissions import ServiceSubmission, ServiceInput
from waves.utils.validators import ServiceInputValidator
import waves.const
import waves.settings


# TODO refactoring for the copy_paste field associated with FileInput (override formfield template ?)
class ServiceForm(forms.ModelForm):
    pass


class ServiceSubmissionForm(forms.ModelForm):
    class Meta:
        model = ServiceSubmission
        fields = ['title', 'email']

    slug = forms.CharField(widget=forms.HiddenInput())
    title = forms.CharField(label="Name your analysis", required=True)
    email = forms.EmailField(label="Mail me results", required=False)

    def __init__(self, *args, **kwargs):
        parent_form = kwargs.pop('parent', None)
        super(ServiceSubmissionForm, self).__init__(*args, **kwargs)
        # print 'Is Bound', self.is_bound
        self.helper = self.get_helper(form_tag=True)
        self.helper.init_layout(fields=('title', 'email', 'slug'))
        self.fields['title'].initial = 'my %s job' % self.instance.service.name
        self.fields['slug'].initial = str(self.instance.slug)
        self.list_inputs = list(self.instance.service_inputs.filter(editable=True).order_by('-mandatory', 'order'))
        extra_fields = []
        for service_input in self.list_inputs:
            if service_input.type == waves.const.TYPE_FILE and not service_input.multiple:
                extra_fields.append(self._create_copy_paste_field(service_input))
                extra_fields.extend(self._create_sample_fields(service_input))

            self.helper.set_field(service_input, self)
            self.helper.set_layout(service_input, self)
            for dependent_input in service_input.dependent_inputs.filter(editable=True):
                # conditional parameters must not be required to use classic django form validation process
                dependent_input.required = False
                if dependent_input.type == waves.const.TYPE_FILE and not dependent_input.multiple:
                    extra_fields.append(self._create_copy_paste_field(dependent_input))
                self.helper.set_field(dependent_input, self)
                self.helper.set_layout(dependent_input, self)
                # extra_fields.append(dependent_input)
        self.list_inputs.extend(extra_fields)
        self.helper.end_layout()

    @staticmethod
    def get_helper(**kwargs):
        try:
            helper = import_string(
                '.'.join(['waves', 'forms', 'lib', waves.settings.WAVES_FORM_PROCESSOR, 'FormHelper']))
            return helper(**kwargs)
        except ImportError:
            raise RuntimeError(
                'Wrong form processor, unable to create any form (%s)' % waves.settings.WAVES_FORM_PROCESSOR)

    def _create_copy_paste_field(self, service_input):
        # service_input.mandatory = False # Field is validated in clean process
        cp_service = copy.copy(service_input)
        cp_service.label = 'Copy/paste content'
        cp_service.description = ''
        cp_service.mandatory = False
        cp_service.type = waves.const.TYPE_TEXT
        cp_service.name = 'cp_' + service_input.name
        self.helper.set_field(cp_service, self)
        self.fields[cp_service.name].widget = forms.Textarea(attrs={'cols': 20, 'rows': 10})
        return cp_service

    def _create_sample_fields(self, service_input):
        extra_fields = []
        if service_input.input_samples.count() > 0:
            for input_sample in service_input.input_samples.all():
                sample_field = copy.copy(service_input)
                sample_field.label = "Sample: " + input_sample.name
                sample_field.value = input_sample.file.name
                sample_field.name = 'sp_' + service_input.name + '_' + str(input_sample.pk)
                sample_field.type = waves.const.TYPE_BOOLEAN
                sample_field.description = ''
                sample_field.mandatory = False
                extra_fields.append(sample_field)
                self.helper.set_field(sample_field, self)
                self.fields[sample_field.name].initial = False
        return extra_fields

    def clean(self):
        # print "in clean"
        cleaned_data = super(ServiceSubmissionForm, self).clean()
        # print cleaned_data
        validator = ServiceInputValidator()
        for data in copy.copy(cleaned_data):
            # print "data", data

            srv_input = next((x for x in self.list_inputs if x.name == data), None)
            sample_selected = False
            # print "srv_input ", srv_input
            if srv_input:
                # posted data correspond to a expected input for service
                posted_data = cleaned_data.get(srv_input.name)
                # print 'posted ', posted_data
                if srv_input.type == waves.const.TYPE_FILE:
                    if srv_input.input_samples.count() > 0:
                        for input_sample in srv_input.input_samples.all():
                            sample_selected = cleaned_data.get('sp_' + srv_input.name + '_' + str(input_sample.pk),
                                                               None)

                            if 'sp_' + srv_input.name in self.cleaned_data:
                                del self.cleaned_data['sp_' + srv_input.name + '_' + str(input_sample.pk)]
                            if sample_selected:
                                sample_selected = input_sample.pk
                                break
                    if not sample_selected:
                        if not cleaned_data.get('cp_' + srv_input.name, False):
                            if srv_input.mandatory and not posted_data:
                                # No posted data in copy/paste but file field is mandatory, so raise error
                                self.add_error(srv_input.name,
                                               ValidationError('You must provide data for %s' % srv_input.label))
                        else:
                            # cp provided, push value in base file field
                            cleaned_data[srv_input.name] = cleaned_data.get('cp_' + srv_input.name)
                    else:
                        cleaned_data[srv_input.name] = sample_selected
                    # Remove all cp_ from posted data
                    if 'cp_' + srv_input.name in self.cleaned_data:
                        del self.cleaned_data['cp_' + srv_input.name]
                else:
                    validator.validate_input(srv_input, posted_data, self)
        return cleaned_data

    def is_valid(self):
        return super(ServiceSubmissionForm, self).is_valid()

