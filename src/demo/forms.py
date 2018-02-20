from __future__ import unicode_literals

import smtplib

from contact_form.forms import ContactForm
from crispy_forms.helper import FormHelper, Layout
from django import forms
from django.contrib import messages
from django.core import validators
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.conf import settings
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


class WDContactForm(ContactForm):

    recipient_list = [settings.CONTACT_EMAIL, ]

    def __init__(self, data=None, files=None, request=None, recipient_list=None, *args, **kwargs):
        super(WDContactForm, self).__init__(data, files, request, recipient_list, *args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            'email',
            'name',
            'body',
            )

    def save(self, fail_silently=False):
        try:
            message_dict = self.get_message_dict()
            send_mail(fail_silently=False, **message_dict)
            messages.success(self.request, "Your message has been successfully sent, we'll get in touch soon")
        except smtplib.SMTPException:
            messages.error(self.request, "Sorry you message was not sent. We are working on it !")
            return False
