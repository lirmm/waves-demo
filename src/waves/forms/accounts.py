from __future__ import unicode_literals
from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.conf import settings
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field
from crispy_forms.bootstrap import PrependedText
from django.contrib.auth import get_user_model
from django_countries.fields import LazyTypedChoiceField
from django_countries import countries
from authtools import forms as authtoolsforms
from django.contrib.auth import forms as authforms
from django.core.urlresolvers import reverse
import registration.forms

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
    # TODO add picture upload (change template pack value for input type file)
    institution = forms.CharField()
    register_for_api = forms.BooleanField('Register as a REST API user')
    country = LazyTypedChoiceField(choices=countries)
    phone = forms.CharField(required=False)
    comment = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': '5'}))

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields["email"].widget.input_type = "email"  # ugly hack
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-4 col-xs-4 hidden-sm hidden-xs'
        self.helper.field_class = 'col-md-8 col-xs-12'
        # self.helper.form_show_labels = False
        self.helper.layout = Layout(
            PrependedText('email', '@', placeholder="Enter Email", autofocus="")
            if 'bootstrap' in settings.CRISPY_TEMPLATE_PACK
            else Field('email', placeholder="Enter Email", autofocus=""),
            Field('name', placeholder="Enter your full name"),
            Field('password1', placeholder="Enter Password"),
            Field('password2', placeholder="Confirm Password"),
            Field('register_for_api', placeholder="Register for our API access"),
            Field('country', placeholder="Select your country", css_class='selectpicker'),
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
