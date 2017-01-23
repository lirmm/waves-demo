from __future__ import unicode_literals

from django.conf.urls import url, include
from rest_framework import routers
# API VIEWS
from waves.api.views import categories, jobs, services
from waves.views.jobs import JobOutputView
from rest_framework.schemas import get_schema_view
from rest_framework.renderers import JSONRenderer
from rest_framework_swagger.views import get_swagger_view
from rest_framework.renderers import CoreJSONRenderer

# API router setup
router = routers.DefaultRouter()
# Services URIs configuration
router.register(prefix=r'categories',
                viewset=categories.CategoryViewSet,
                base_name='waves-services-category')
router.register(prefix=r'services',
                viewset=services.ServiceViewSet,
                base_name='waves-services')
# Jobs URIs configuration
router.register(prefix=r'jobs',
                viewset=jobs.JobViewSet,
                base_name='waves-jobs')

swagger_doc_schema_view = get_swagger_view(title='WAVES Application REST API')
schema_view = get_schema_view(
    title='WAVES Application REST API',
    renderer_classes=[CoreJSONRenderer]
)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^docs/html/', include('rest_framework_docs.urls')),
    url(r'^docs/swagger/$', swagger_doc_schema_view),
    url(r'^services/(?P<service>[^/.]+)/submissions/(?P<api_name>[^/.]+)/$',
        services.ServiceJobSubmissionView.as_view(), name='waves-services-submissions'),
    url(r'^services/(?P<service>[^/.]+)/submissions/(?P<api_name>[^/.]+)/form/',
        services.ServiceJobSubmissionViewForm.as_view(), name='waves-services-submissions-form'),
    url(r'^jobs/outputs/(?P<slug>[\w-]+)/$', JobOutputView.as_view(), name="job-api-output"),
]
