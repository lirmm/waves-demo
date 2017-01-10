""" WAVES user accounts urls """
from __future__ import unicode_literals
from django.conf.urls import url
from django.views.generic import TemplateView

import accounts.views

urlpatterns = [
    url(r'^activate/complete/$',
        accounts.views.ActivationView.as_view(template_name='accounts/activation_complete.html'),
        name='registration_activation_complete'),
    url(r'^activate/(?P<activation_key>[-:\w]+)/$', accounts.views.ActivationView.as_view(),
        name='registration_activate'),
    url(r'^register/$', accounts.views.SignUpView.as_view(), name='registration_register'),
    url(r'^register/complete/$', TemplateView.as_view(template_name='accounts/registration_complete.html'),
        name='registration_complete'),
    url(r'^register/closed/$', TemplateView.as_view(template_name='accounts/registration_closed.html'),
        name='registration_disallowed'),
    url(r'^signup/$', accounts.views.SignUpView.as_view(), name='signup'),
    url(r'^password/change/$', accounts.views.PasswordChangeView.as_view(), name='password-change'),
    url(r'^password/reset/$', accounts.views.PasswordResetView.as_view(), name='password-reset'),
    url(r'^password/reset/done/$', accounts.views.PasswordResetDoneView.as_view(), name='password-reset-done'),
    url(r'^password/reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$$',
        accounts.views.PasswordResetConfirmView.as_view(),
        name='password-reset-confirm'),
    url(r'^login/$', accounts.views.LoginView.as_view(), name="login"),
    url(r'^logout/$', accounts.views.LogoutView.as_view(), name='logout'),
]
