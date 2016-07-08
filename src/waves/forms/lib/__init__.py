from __future__ import unicode_literals

from functools import partial, wraps

from django import forms

import waves.const as const
from waves.models import ServiceInput, Service


class BaseHelper(object):
    @staticmethod
    def get_field_for_type(service_input):
        if service_input.type == const.TYPE_FILE:
            # TODO manage multiple file input
            """
            if service_input.multiple:
                form_field = forms.models.inlineformset_factory(model=ServiceInput, parent_model=Service,
                                                                form=FileInputForm)
                # form=wraps(FileInputForm)(partial(FileInputForm, service_input=service_input))
            else:
            """
            form_field = forms.FileField(label=service_input.label,
                                         required=service_input.mandatory,
                                         help_text=service_input.description)
        elif service_input.type == const.TYPE_BOOLEAN:
            form_field = forms.BooleanField(label=service_input.label,
                                            initial=service_input.default,
                                            required=False,
                                            help_text=service_input.description)
        elif service_input.type == const.TYPE_LIST:
            if not service_input.multiple:
                form_field = forms.ChoiceField(label=service_input.label,
                                               choices=service_input.get_choices(),
                                               initial=service_input.default,
                                               required=service_input.mandatory,
                                               help_text=service_input.description)
                if service_input.display == const.DISPLAY_RADIO:
                    form_field.widget = forms.RadioSelect()
                elif service_input.display == const.DISPLAY_CHECKBOX:
                    form_field.widget = forms.CheckboxChoiceInput()
            else:
                form_field = forms.MultipleChoiceField(label=service_input.label,
                                                       choices=service_input.get_choices(),
                                                       initial=service_input.default,
                                                       required=service_input.mandatory,
                                                       help_text=service_input.description)
                if service_input.display == const.DISPLAY_CHECKBOX:
                    form_field.widget = forms.CheckboxSelectMultiple()

            form_field.css_class = 'text-left'
        elif service_input.type == const.TYPE_INTEGER:
            form_field = forms.IntegerField(initial=service_input.default,
                                            label=service_input.label,
                                            required=service_input.mandatory,
                                            min_value=service_input.get_min(),
                                            max_value=service_input.get_max(),
                                            help_text=service_input.description)
        elif service_input.type == const.TYPE_FLOAT:
            form_field = forms.FloatField(initial=service_input.default,
                                          label=service_input.label,
                                          required=service_input.mandatory,
                                          min_value=service_input.get_min(),
                                          max_value=service_input.get_max(),
                                          help_text=service_input.description)
        elif service_input.type == const.TYPE_TEXT:
            form_field = forms.CharField(max_length=100,
                                         label=service_input.label,
                                         required=service_input.mandatory,
                                         initial=service_input.default,
                                         help_text=service_input.description)
        else:
            raise Exception('Error wrong data type to service_input !' + service_input.type)

        """
        if hasattr(service_input, 'related_to'):
            value_for = service_input.get_value_for_choice(service_input.when_value)
            form_field.label = '%s for %s "%s"' % (form_field.label, service_input.related_to.label, value_for)
            form_field.help_text = 'When %s is "%s"' % (service_input.related_to.label, value_for)
            form_field.required = False
        """
        return form_field

    @staticmethod
    def get_field_layout(service_input):
        raise NotImplementedError()

    def render_layout(self):
        raise NotImplementedError()


class FileInputForm(forms.ModelForm):
    class Meta:
        model = ServiceInput
        exclude = ['pk']

    def __init__(self, *args, **kwargs):
        """
        parameters from parent : data, files, auto_id, prefix, initial, error_class, label_suffix, empty_permitted,
            field_order
        Args:
            *args:
            **kwargs:
        """
        self.input = kwargs.pop('service_input')
        assert isinstance(self.input, ServiceInput)
        super(FileInputForm, self).__init__(*args, **kwargs)
        self.fields[self.input.name] = forms.FileField(label=self.input.label, required=self.input.mandatory,
                                                       help_text=self.input.description, initial=self.input.default)
