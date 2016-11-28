""" WAVES back-office dedicated URLs
"""
from __future__ import unicode_literals

from django.conf.urls import url
from waves.views.admin import *
from django.contrib.auth.decorators import login_required

urlpatterns = [
    url(r'^service/(?P<service_id>\d+)/import$', login_required(ServiceParamImportView.as_view()),
        name="service_import_form"),
    url(r'^runner/(?P<runner_id>\d+)/import$', login_required(RunnerImportToolView.as_view()),
        name="runner_import_form"),
    url(r'^service/(?P<service_id>\d+)/duplicate$', login_required(ServiceDuplicateView.as_view()),
        name="service_duplicate"),
    url(r'^job/(?P<job_id>[0-9]+)/cancel/$', login_required(JobCancelView.as_view()),
        name='job_cancel'),
    url(r'^service/(?P<pk>\d+)/export$', login_required(ServiceExportView.as_view()),
        name="service_export_form"),
    url(r'^runner/(?P<pk>\d+)/export$', login_required(RunnerExportView.as_view()),
        name="runner_export_form"),
    url(r'^runner/(?P<pk>\d+)/check$', login_required(RunnerTestConnectionView.as_view()),
        name="runner_test_connection"),

]
