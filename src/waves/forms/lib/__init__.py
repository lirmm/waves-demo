from __future__ import unicode_literals

from multiupload.fields import MultiFileField
from django import forms

import waves.const as const


class BaseHelper(object):

    def set_field(self, service_input, form):
        field_dict = dict(
            label=service_input.label,
            required=service_input.mandatory,
            help_text=service_input.description,
            initial=service_input.default
        )
        if service_input.type == const.TYPE_FILE:
            # TODO manage multiple file input
            if service_input.multiple:
                field_dict.update(dict(min_num=1, max_file_size=1024*5))
            else:
                field_dict.update(dict(max_num=1))
            form_field = MultiFileField(**field_dict)
        elif service_input.type == const.TYPE_BOOLEAN:
            field_dict.update(dict(required=False))
            form_field = forms.BooleanField(**field_dict)
        elif service_input.type == const.TYPE_LIST:
            field_dict.update(dict(choices=service_input.get_choices()))
            if not service_input.multiple:
                form_field = forms.ChoiceField(**field_dict)
                if service_input.display == const.DISPLAY_RADIO:
                    form_field.widget = forms.RadioSelect()
            else:
                form_field = forms.MultipleChoiceField(**field_dict)
                if service_input.display == const.DISPLAY_CHECKBOX:
                    form_field.widget = forms.CheckboxSelectMultiple()
            form_field.css_class = 'text-left'
        elif service_input.type == const.TYPE_INTEGER:
            field_dict.update(dict(min_value=service_input.get_min(),
                                   max_value=service_input.get_max()))
            form_field = forms.IntegerField(**field_dict)
        elif service_input.type == const.TYPE_FLOAT:
            field_dict.update(dict(min_value=service_input.get_min(),
                                   max_value=service_input.get_max()))
            form_field = forms.FloatField(**field_dict)
        elif service_input.type == const.TYPE_TEXT:
            field_dict.update(dict(max_length=255))
            form_field = forms.CharField(**field_dict)
        else:
            raise Exception('Error wrong data type to service_input !' + service_input.type)
        #if hasattr(service_input, 'related_to') and service_input.when_value != service_input.related_to.default:
        #    print "update display for ", service_input
        #    form_field.widget.attrs.update(dict(style='display:none'))
        form.fields[service_input.name] = form_field

    def set_layout(self, service_input):
        raise NotImplementedError()

    def init_layout(self):
        pass

    def end_layout(self):
        pass


class FileInputForm(forms.ModelForm):
    """
    Specific file input form element, added with a copy/paste content aside in layout
    """
    pass
