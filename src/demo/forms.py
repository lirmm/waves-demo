from __future__ import unicode_literals

from django import forms
from django.core import validators
from django.core.exceptions import ValidationError

from demo.models import ServiceMeta


class ServiceMetaForm(forms.ModelForm):
    class Meta:
        model = ServiceMeta
        exclude = ['order']

    def clean(self):
        cleaned_data = super(ServiceMetaForm, self).clean()
        try:
            validator = validators.URLValidator()
            validator(cleaned_data['value'])
            self.instance.is_url = True
        except ValidationError as e:
            if self.instance.type in (self.instance.META_WEBSITE, self.instance.META_DOC, self.instance.META_DOWNLOAD):
                raise e

