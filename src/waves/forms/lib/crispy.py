from __future__ import unicode_literals

from crispy_forms.helper import FormHelper as BaseFormHelper
from crispy_forms.layout import *
from crispy_forms.bootstrap import FormActions
from django import forms

from waves.forms.lib import BaseHelper

import waves.const as const

__all__ = ['FormHelper', 'FormLayout']


class FormHelper(BaseFormHelper, BaseHelper):
    """
    Extended FormHelper based on crispy FormHelper,
    Dynamic form fields according to inputs types and parameters
    """

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

    def set_layout(self, service_input):
        """

        Args:
            service_input:
            hidden:

        Returns:

        """
        css_class = ""
        wrapper_class = ""
        field_id = "id_" + service_input.name
        dependent_on = ""
        dependent_4_value = ""
        if service_input.dependent_inputs.count() > 0:
            print 'has dependents ? ', service_input
            css_class = "has_dependent"
        if hasattr(service_input, 'related_to'):
            field_id += '_' + service_input.related_to.name + '_' + service_input.when_value
            dependent_on = service_input.related_to.name
            dependent_4_value = service_input.when_value
            if service_input.when_value != service_input.related_to.default:
                wrapper_class = "hid_dep_parameter"
            else:
                wrapper_class = "dis_dep_parameter"
        print "Field ", service_input
        input_field = Field(service_input.name,
                            css_class=css_class,
                            id=field_id,
                            title=service_input.description,
                            wrapper_class=wrapper_class,
                            dependent_on=dependent_on,
                            dependent_4_value=dependent_4_value
                            )

        self.layout.append(
            input_field
        )

    def init_layout(self):
        self.layout = Layout(
            Field('title'),
            HTML('<HR/>')
        )

    def end_layout(self):
        self.layout.extend([
            HTML('<HR/>'),
            Field('email', ),
            FormActions(
                Reset('reset', 'Reset form'),
                Submit('save', 'Submit a job')
            )
        ])
