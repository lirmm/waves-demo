from __future__ import unicode_literals

from braces import views as bracesviews

from authtools import views as authviews
from django.conf import settings
from django.db import transaction
from django.contrib import auth, messages
from django.contrib.auth import get_user_model
from smtplib import SMTPException
from django.core.urlresolvers import reverse_lazy
from django.views import generic

from registration.backends.hmac.views import RegistrationView, ActivationView as BaseActivationView
from base import WavesBaseContextMixin
from waves.forms.accounts import *
import waves.settings
User = get_user_model()


class LoginView(bracesviews.AnonymousRequiredMixin,
                authviews.LoginView, WavesBaseContextMixin):
    template_name = "accounts/login.html"
    form_class = LoginForm

    def form_valid(self, form):
        redirect = super(LoginView, self).form_valid(form)
        remember_me = form.cleaned_data.get('remember_me')
        if remember_me is True:
            one_month = 30 * 24 * 60 * 60
            expiry = getattr(settings, "KEEP_LOGGED_DURATION", one_month)
            self.request.session.set_expiry(expiry)
        return redirect


class LogoutView(authviews.LogoutView, WavesBaseContextMixin):
    url = reverse_lazy('waves:home')

    def get(self, *args, **kwargs):
        auth.logout(self.request)
        messages.success(self.request,
                         "Your successfully log-out")
        return super(LogoutView, self).get(*args, **kwargs)


class SignUpView(bracesviews.AnonymousRequiredMixin,
                 bracesviews.FormValidMessageMixin,
                 generic.CreateView,
                 RegistrationView,
                 WavesBaseContextMixin):
    form_class = SignupForm
    model = User
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('waves:registration_complete')
    form_valid_message = "You are now registered, don't forget to activate !"
    email_body_template = 'accounts/emails/activation_email.txt'
    email_subject_template = 'accounts/emails/activation_email_subject.txt'
    disallowed_url = 'waves:registration_disallowed'

    def get_success_url(self, user):
        return ('waves:registration_complete', (), {})

    @transaction.atomic()
    def create_inactive_user(self, form):
        try:
            new_user = super(SignUpView, self).create_inactive_user(form)
            new_user.profile.country = form.cleaned_data.get('country')
            new_user.profile.institution = form.cleaned_data.get('institution')
            new_user.profile.phone = form.cleaned_data.get('phone')
            new_user.profile.comment = form.cleaned_data.get('comment')
            new_user.profile.registered_for_api = form.cleaned_data.get('register_for_api')
            new_user.profile.save()
            return new_user
        except SMTPException as e:
            messages.error(self.request, "Something went wrong with your registration, contact team for more info")
            raise e

    def registration_allowed(self):
        return waves.settings.WAVES_REGISTRATION_ALLOWED


class PasswordChangeView(authviews.PasswordChangeView, WavesBaseContextMixin):
    form_class = PasswordChangeForm
    template_name = 'accounts/password_change.html'
    success_url = reverse_lazy('waves:home')

    def form_valid(self, form):
        form.save()
        messages.success(self.request,
                         "Your password was changed, "
                         "hence you have been logged out. Please re-login")
        return super(PasswordChangeView, self).form_valid(form)


class PasswordResetView(authviews.PasswordResetView, WavesBaseContextMixin):
    form_class = PasswordResetForm
    template_name = 'accounts/password_reset.html'
    success_url = reverse_lazy('waves:password-reset-done')
    subject_template_name = 'accounts/emails/password_reset_subject.txt'
    email_template_name = 'accounts/emails/password_reset_email.html'


class PasswordResetDoneView(authviews.PasswordResetDoneView, WavesBaseContextMixin):
    template_name = 'accounts/password_reset_done.html'


class PasswordResetConfirmView(authviews.PasswordResetConfirmAndLoginView, WavesBaseContextMixin):
    template_name = 'accounts/password_reset_confirm.html'
    form_class = SetPasswordForm


class ActivationView(BaseActivationView, WavesBaseContextMixin):
    template_name = 'accounts/activate.html'

    @transaction.atomic
    def activate(self, *args, **kwargs):
        user = super(ActivationView, self).activate(*args, **kwargs)
        return user

    def get_success_url(self, user):
        return ('waves:registration_activation_complete', (), {})
