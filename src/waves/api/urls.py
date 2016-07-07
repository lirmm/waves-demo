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
                base_name='servicetoolcategory')
router.register(prefix=r'services',
                viewset=services.ServiceViewSet,
                base_name='servicetool')
router.register(prefix=r'services/(?P<service>[0-9]+)/inputs',
                viewset=services.ServiceInputViewSet,
                base_name='servicetoolinput')
# Jobs URIs configuration
router.register(prefix=r'jobs',
                viewset=jobs.JobViewSet,
                base_name='servicejob')

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^token-auth/', obtain_jwt_token),
    url(r'^docs/', include('rest_framework_docs.urls')),
]
