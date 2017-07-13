""" User Accounts views """
from smtplib import SMTPException

from authtools import views as authviews
from braces import views as bracesviews
from django.conf import settings
from django.contrib import auth, messages
from django.contrib.auth import get_user_model
from django.core import signing
from django.db import transaction
# Create your views here.
from django.urls import reverse_lazy
from django.views import generic
from registration.backends.hmac.views import RegistrationView, ActivationView as BaseActivationView

from accounts.forms import *
from waves.wcore.settings import waves_settings

User = get_user_model()


class LoginView(bracesviews.AnonymousRequiredMixin,
                authviews.LoginView):
    """ Login view """
    template_name = "accounts/login.html"
    success_url = reverse_lazy("home")
    form_class = LoginForm

    def form_valid(self, form):
        """ Log in User for current session """
        redirect = super(LoginView, self).form_valid(form)
        remember_me = form.cleaned_data.get('remember_me')
        if remember_me is True:
            one_month = 30 * 24 * 60 * 60
            expiry = getattr(settings, "KEEP_LOGGED_DURATION", one_month)
            self.request.session.set_expiry(expiry)
        return redirect


class LogoutView(authviews.LogoutView):
    """ User logout view """
    url = reverse_lazy('home')

    def get(self, *args, **kwargs):
        """ logout user from WAVES """
        auth.logout(self.request)
        messages.success(self.request, "Your successfully log-out")
        return super(LogoutView, self).get(*args, **kwargs)


class SignUpView(bracesviews.AnonymousRequiredMixin, bracesviews.FormValidMessageMixin, generic.CreateView,
                 RegistrationView):
    """ User Registration view """
    form_class = SignupForm
    model = User
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('accounts:registration_complete')
    form_valid_message = "You are now registered, don't forget to activate !"
    email_body_template = 'accounts/emails/activation_email.txt'
    email_subject_template = 'accounts/emails/activation_email_subject.txt'
    disallowed_url = 'accounts:registration_disallowed'

    def get_success_url(self, user):
        """ Redirect to registration complete when done """
        return 'accounts:registration_complete', (), {}

    @transaction.atomic()
    def create_inactive_user(self, form):
        """ Create a inactive user when form is submitted, send mail to user with activation link """
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
        """ set if User registration is currently allowed """
        return waves_settings.REGISTRATION_ALLOWED

    def get_email_context(self, activation_key):
        """ Setup activation link for registration confirmation mail """
        context = super(SignUpView, self).get_email_context(activation_key)
        context['brand_name'] = waves_settings.APP_NAME
        return context


class PasswordChangeView(authviews.PasswordChangeView):
    """ User password change view """
    form_class = PasswordChangeForm
    template_name = 'accounts/password_change.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        """ Form process when valid"""
        form.save()
        messages.success(self.request,
                         "Your password was successfully changed")
        return super(PasswordChangeView, self).form_valid(form)


class PasswordResetView(authviews.PasswordResetView):
    """ User password reset form view """
    form_class = PasswordResetForm
    template_name = 'accounts/password_reset.html'
    success_url = reverse_lazy('accounts:password-reset-done')
    subject_template_name = 'accounts/emails/password_reset_subject.txt'
    email_template_name = 'accounts/emails/password_reset_email.html'


class PasswordResetDoneView(authviews.PasswordResetDoneView):
    """ Reset password done view """
    template_name = 'accounts/password_reset_done.html'


class PasswordResetConfirmView(authviews.PasswordResetConfirmAndLoginView):
    """ Reset password confirmation """
    template_name = 'accounts/password_reset_confirm.html'
    form_class = SetPasswordForm


class ActivationView(BaseActivationView):
    """ User account activation view """
    template_name = 'accounts/activate.html'
    error_reason = ''

    @transaction.atomic
    def activate(self, *args, **kwargs):
        """ Activate user account with specified key"""
        user = super(ActivationView, self).activate(*args, **kwargs)
        if user is False:
            pass
        return user

    def get_context_data(self, **kwargs):
        context = super(ActivationView, self).get_context_data(**kwargs)
        context['error_reason'] = self.error_reason
        return context

    def validate_key(self, activation_key):
        try:
            username = signing.loads(
                activation_key,
                salt=settings.REGISTRATION_SALT,
                max_age=settings.ACCOUNT_ACTIVATION_DAYS * 86400
            )
            return username
        # SignatureExpired is a subclass of BadSignature, so this will
        # catch either one.
        except signing.SignatureExpired:
            self.template_name = "accounts/activation_error.html"
            self.error_reason = "Your code has expired"
            return None
        except signing.BadSignature:
            self.template_name = "accounts/activation_error.html"
            self.error_reason = "Bad activation key"
            return None

    def get_success_url(self, user):
        """ Redirect to activation complete view upon activation success """
        return 'accounts:registration_activation_complete', (), {}
