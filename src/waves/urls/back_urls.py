from __future__ import unicode_literals

from django.conf.urls import url
from django.conf.urls import include
from waves.views.admin import *

urlpatterns = [
    url(r'^admin/import/(?P<service_id>\d+)/$', ServiceParamImportView.as_view(),
        name="service_import_form"),
    url(r'^admin/services/duplicate/(?P<service_id>\d+)/$', ServiceDuplicateView.as_view(),
        name="service_duplicate"),
    url(r'^admin/job/(?P<job_id>[0-9]+)/cancel/$', JobCancelView.as_view(), name='job_cancel'),
]
