from __future__ import unicode_literals

from django.conf.urls import url, include
from rest_framework import routers

# API VIEWS
from .views import categories, jobs, services
from rest_framework_jwt.views import obtain_jwt_token

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

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^token-auth/', obtain_jwt_token),
    url(r'^docs/', include('rest_framework_docs.urls')),
]
