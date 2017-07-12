from __future__ import unicode_literals

import registration.forms
from authtools import forms as authtoolsforms
from crispy_forms.bootstrap import PrependedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, HTML, Field
from django import forms
from django.conf import settings
from django.contrib.auth import forms as authforms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.core.urlresolvers import reverse
from django.core.validators import RegexValidator
from django_countries import countries
from django_countries.fields import LazyTypedChoiceField

__all__ = ['LoginForm', 'SignupForm', 'PasswordChangeForm', 'PasswordResetForm', 'SetPasswordForm']
User = get_user_model()


class LoginForm(AuthenticationForm):
    remember_me = forms.BooleanField(required=False, initial=False)

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields["username"].widget.input_type = "email"  # ugly hack

        self.helper.layout = Layout(
            Field('username', placeholder="Enter Email", autofocus=""),
            Field('password', placeholder="Enter Password"),
            HTML('<a href="{}">Forgot Password?</a>'.format(
                reverse("accounts:password-reset"))),
            Field('remember_me'),
            Submit('sign_in', 'Log in',
                   css_class="btn btn-lg btn-primary btn-block"),
        )


class SignupForm(registration.forms.RegistrationFormTermsOfService,
                 registration.forms.RegistrationFormUniqueEmail):
    class Meta(registration.forms.RegistrationFormTermsOfService.Meta):
        model = User
        fields = (User.USERNAME_FIELD,) + tuple(User.REQUIRED_FIELDS) + ('tos',)

    # Override default labels en help text from registration
    email = forms.EmailField(
        help_text='',
        required=True
    )
    tos = forms.BooleanField(
        widget=forms.CheckboxInput,
        label='I have read and agree to the '
              '<a href="#" data-toggle="modal" data-target="#tosModal">Terms of Service</a>,',
    )
    institution = forms.CharField()
    register_for_api = forms.BooleanField(label='Register as a REST API user', initial=False, required=False)
    country = LazyTypedChoiceField(choices=countries)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                 message="Phone number must be entered in the format: '+999999999'. "
                                         "Up to 15 digits allowed.")
    phone = forms.CharField(required=False, validators=[phone_regex])
    comment = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': '5'}))

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields["email"].widget.input_type = "email"  # ugly hack
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-4 col-xs-4 hidden-sm hidden-xs'
        self.helper.field_class = 'col-md-8 col-xs-12'
        # self.helper.form_show_labels = False
        if 'bootstrap' in settings.CRISPY_TEMPLATE_PACK:
            email_field = PrependedText('email', '@', placeholder="Enter Email", autofocus="")
        else:
            email_field = Field('email', placeholder="Enter Email", autofocus="")
        self.helper.layout = Layout(
            email_field,
            Field('name', placeholder="Enter your full name"),
            Field('password1', placeholder="Enter Password"),
            Field('password2', placeholder="Confirm Password"),
            Field('register_for_api', placeholder="Register for our API access"),
            Field('country', placeholder="Select your country"),
            Field('institution', placeholder="Your institution"),
            Field('phone', placeholder="Phone"),
            Field('comment', placeholder="Any comment ?"),
            Field('tos', ),
            Submit('sign_up', 'Sign up', css_class="btn btn-lg btn-primary btn-block"),
        )


class PasswordChangeForm(authforms.PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super(PasswordChangeForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()

        self.helper.layout = Layout(
            Field('old_password', placeholder="Enter old password",
                  autofocus=""),
            Field('new_password1', placeholder="Enter new password"),
            Field('new_password2', placeholder="Enter new password (again)"),
            Submit('pass_change', 'Change Password', css_class="btn-warning"),
        )


class PasswordResetForm(authtoolsforms.FriendlyPasswordResetForm):
    def __init__(self, *args, **kwargs):
        super(PasswordResetForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()

        self.helper.layout = Layout(
            Field('email', placeholder="Enter email",
                  autofocus=""),
            Submit('pass_reset', 'Reset Password', css_class="btn-warning"),
        )


class SetPasswordForm(authforms.SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super(SetPasswordForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()

        self.helper.layout = Layout(
            Field('new_password1', placeholder="Enter new password",
                  autofocus=""),
            Field('new_password2', placeholder="Enter new password (again)"),
            Submit('pass_change', 'Change Password', css_class="btn-warning"),
        )
