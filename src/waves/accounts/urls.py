from __future__ import unicode_literals
from django.conf.urls import include, url
from django.views.generic import TemplateView

import waves.views.accounts

urlpatterns = [
    url(r'^activate/complete/$',
        waves.views.accounts.ActivationView.as_view(template_name='accounts/activation_complete.html'),
        name='registration_activation_complete'),
    url(r'^activate/(?P<activation_key>[-:\w]+)/$',
        waves.views.accounts.ActivationView.as_view(),
        name='registration_activate'),
    url(r'^register/$',
        waves.views.accounts.SignUpView.as_view(),
        name='registration_register'),
    url(r'^register/complete/$',
        TemplateView.as_view(template_name='accounts/registration_complete.html'),
        name='registration_complete'),
    url(r'^register/closed/$',
        TemplateView.as_view(template_name='accounts/registration_closed.html'),
        name='registration_disallowed'),
    url(r'^login/$', waves.views.accounts.LoginView.as_view(), name="login"),
    url(r'^logout/$', waves.views.accounts.LogoutView.as_view(), name='logout'),
    url(r'^signup/$', waves.views.accounts.SignUpView.as_view(), name='signup'),
    url(r'^password/change/$', waves.views.accounts.PasswordChangeView.as_view(), name='password-change'),
    url(r'^password/reset/$', waves.views.accounts.PasswordResetView.as_view(), name='password-reset'),
    url(r'^password/reset/done/$', waves.views.accounts.PasswordResetDoneView.as_view(), name='password-reset-done'),
    url(r'^password/reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$$',
        waves.views.accounts.PasswordResetConfirmView.as_view(),
        name='password-reset-confirm'),
]
