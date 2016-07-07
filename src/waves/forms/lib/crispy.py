from __future__ import unicode_literals

from crispy_forms.helper import FormHelper as BaseFormHelper
from crispy_forms.layout import *
from crispy_forms.bootstrap import FormActions

from waves.forms.lib import BaseHelper
import waves.const as const

__all__ = ['FormHelper', 'FormLayout']


class FormHelper(BaseFormHelper, BaseHelper):
    def __init__(self, form=None, **kwargs):
        form_tag = kwargs.pop('form_tag', True)
        form_class = kwargs.pop('form_class', 'form-horizontal')
        label_class = kwargs.pop('label_class', 'col-lg-4')
        field_class = kwargs.pop('field_class', 'col-lg-8 text-left')
        super(FormHelper, self).__init__(form)
        self.form_tag = form_tag
        self.form_class = form_class
        self.label_class = label_class
        self.field_class = field_class
        self.render_unmentioned_fields = True
        self.layout = Layout()

    def get_field_layout(self, service_input, hidden=False):
        """

        Args:
            service_input:
            hidden:

        Returns:

        """
        field_layout = []

        if service_input.type == const.TYPE_FILE:
            input_field = Field(service_input.name, css_class='tool-tip',
                                id='id_' + service_input.name,
                                title=service_input.description)
        elif service_input.type == const.TYPE_BOOLEAN:
            input_field = Field(service_input.name, title=service_input.description)
        elif service_input.type == const.TYPE_LIST:
            input_field = Field(service_input.name, title=service_input.description)
        elif service_input.type == const.TYPE_INTEGER:
            input_field = Field(service_input.name, title=service_input.description)
        elif service_input.type == const.TYPE_FLOAT:
            input_field = Field(service_input.name, title=service_input.description)
        elif service_input.type == const.TYPE_TEXT:
            input_field = Field(service_input.name, title=service_input.description)
        else:
            raise Exception('Error wrong data type to layout !' + service_input.type)
        if hidden:
            input_field.css_class = 'hidden'
        self.layout.append(input_field)
        # add dependent parameters
        for dependent_input in service_input.dependent_inputs.all():
            self.layout.extend(self.get_field_layout(dependent_input, hidden=True))

        return field_layout

    def set_layout(self, list_input):
        self.layout.extend([
            Field('title'),
            HTML('<HR/>')
        ])
        for form_input in list_input:
            self.layout.extend(self.get_field_layout(form_input))
        self.layout.extend([
            HTML('<HR/>'),
            Field('email', ),
            FormActions(Submit('save', 'Submit a job'))
        ])
