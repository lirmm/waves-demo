""" User Profiles forms """
from __future__ import unicode_literals

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Fieldset, Div, Submit
from django import forms
from django_countries.widgets import CountrySelectWidget
from profiles.models import UserProfile
from django.contrib.auth import get_user_model

User = get_user_model()


class UserForm(forms.ModelForm):
    """ Front end model User Form """

    class Meta:
        model = User
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Field('name'),
        )


class ProfileForm(forms.ModelForm):
    """ Front end Admin Form """

    class Meta:
        model = UserProfile
        fields = ['api_key', 'registered_for_api', 'banned', 'comment', 'ip', 'country', 'comment', 'institution']

    widgets = {
        'country': CountrySelectWidget()
    }


class FrontUserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-4'
        self.helper.field_class = 'col-lg-8'
        self.helper.layout = Layout(
            Field('name'),
            Field('email'),
        )

    class Meta:
        model = User
        fields = ['name', 'email']


class FrontProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['registered_for_api', 'country', 'comment', 'institution', 'phone', 'picture']

    delete_profile = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super(FrontProfileForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-4'
        self.helper.field_class = 'col-lg-8'
        self.helper.layout = Layout(
            # Div('picture', css_class='btn-file'),
            Fieldset("Details",
                     'institution',
                     'country',
                     'phone',
                     'picture'),
            Field('comment'),
            Div(
                Submit('delete_profile', 'Delete your account',
                       css_class='btn-danger btn btn-md',
                       type="submit",
                       data_placement="left",
                       data_toggle='confirmation'),
                Submit('update', 'Update', css_class="btn btn-md btn-primary center"),
                css_class='pull-right',
                style='margin-top:1%; margin-right:1%'
            )
        )
