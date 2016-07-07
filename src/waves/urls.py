# Classic Routers
from __future__ import unicode_literals

from django.conf.urls import url
from django.views.generic import TemplateView

from waves.views.admin import ServiceParamImportView, ServiceDuplicateView, JobCancelView
from waves.views.jobs import JobView, JobListView, JobOutputView, JobInputView
from waves.views.services import ServiceDetailView, CategoryListView, CategoryDetailView, JobSubmissionView

urlpatterns = [
    url(r'^admin/import/(?P<service_id>\d+)/$', ServiceParamImportView.as_view(),
        name="service_import_form"),
    url(r'^admin/services/duplicate/(?P<service_id>\d+)/$', ServiceDuplicateView.as_view(),
        name="service_duplicate"),
    url(r'^admin/job/(?P<job_id>[0-9]+)/cancel/$', JobCancelView.as_view(), name='job_cancel'),
    url(r'^services/$', CategoryListView.as_view(), name='services_list'),
    url(r'^category/(?P<pk>[0-9]+)/$', CategoryDetailView.as_view(), name='category_details'),
    url(r'^services/(?P<pk>[0-9]+)/$', ServiceDetailView.as_view(), name='service_details'),
    url(r'^services/(?P<pk>[0-9]+)/create$', JobSubmissionView.as_view(), name='job_submission'),
    url(r'^jobs/(?P<slug>[\w-]+)/$', JobView.as_view(), name="job_details"),
    # TODO merge theses urls into one url / one class on both Models (JobInput / JobOutput)
    url(r'^jobs/inputs/(?P<slug>[\w-]+)/$', JobInputView.as_view(), name="job_input"),
    url(r'^jobs/outputs/(?P<slug>[\w-]+)/$', JobOutputView.as_view(), name="job_output"),
    url(r'^users/jobs/$', JobListView.as_view(), name="job_list"),
    url(r'^rest-services/$', TemplateView.as_view(template_name='rest/rest_api.html'), name='rest_services'),
]
