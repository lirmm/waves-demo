from __future__ import unicode_literals

from django.conf.urls import url
from django.views.generic import TemplateView
from waves.views.jobs import *
from waves.views.services import *
from waves.views.base import *

urlpatterns = [
    url(r'^about/$', AboutPage.as_view(), name='about'),
    url(r'^services/$', CategoryListView.as_view(), name='services_list'),
    url(r'^category/(?P<pk>[0-9]+)/$', CategoryDetailView.as_view(), name='category_details'),
    url(r'^services/(?P<pk>[0-9]+)/$', ServiceDetailView.as_view(), name='service_details'),
    url(r'^services/(?P<pk>[0-9]+)/create$', JobSubmissionView.as_view(), name='job_submission'),
    url(r'^unauthorized/$', HTML403.as_view(), name="unauthorized"),
    url(r'^jobs/(?P<slug>[\w-]+)/$', JobView.as_view(), name="job_details"),
    url(r'^jobs/inputs/(?P<slug>[\w-]+)/$', JobInputView.as_view(), name="job_input"),
    url(r'^jobs/outputs/(?P<slug>[\w-]+)/$', JobOutputView.as_view(), name="job_output"),
    url(r'^rest-services/$', RestServices.as_view(), name='rest_services'),
]
