from __future__ import unicode_literals

from multiupload.fields import MultiFileField
from django import forms
import waves.settings
import waves.const as const
from waves.models.inputs import *


class BaseHelper(object):

    @staticmethod
    def set_field(service_input, form):
        assert isinstance(service_input, BaseParam)
        field_dict = dict(
            label=service_input.label,
            required=service_input.required is True,
            help_text=service_input.help_text,
            initial=form.data.get(service_input.name, service_input.default)
        )
        if isinstance(service_input, FileInput):
            field_dict.update(dict(allow_empty_file=False, required=False))
            if service_input.multiple:
                field_dict.update(dict(min_num=1, max_file_size=waves.settings.WAVES_UPLOAD_MAX_SIZE))
                form_field = MultiFileField(**field_dict)
            else:
                form_field = forms.FileField(**field_dict)
        elif isinstance(service_input, BooleanParam):
            field_dict.update(dict(required=False,
                                   initial=form.data.get(service_input.name, service_input.default)))
            form_field = forms.BooleanField(**field_dict)
        elif isinstance(service_input, ListParam):
            field_dict.update(dict(choices=service_input.choices))
            if not service_input.multiple:
                form_field = forms.ChoiceField(**field_dict)
                if service_input.list_mode == const.DISPLAY_RADIO:
                    form_field.widget = forms.RadioSelect()
            else:
                form_field = forms.MultipleChoiceField(**field_dict)
                if service_input.list_mode == const.DISPLAY_CHECKBOX:
                    form_field.widget = forms.CheckboxSelectMultiple()
            form_field.css_class = 'text-left'
        elif isinstance(service_input, IntegerParam) or isinstance(service_input, DecimalParam):
            field_dict.update(dict(min_value=service_input.get_min(),
                                   max_value=service_input.get_max()))
            form_field = forms.IntegerField(**field_dict)
        else:
            form_field = forms.CharField(**field_dict)
        form.fields[service_input.name] = form_field

    def set_layout(self, service_input):
        raise NotImplementedError()

    def init_layout(self, fields):
        pass

    def end_layout(self):
        pass
