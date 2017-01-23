from __future__ import unicode_literals

from django.conf.urls import url
from django.conf.urls import include


urlpatterns = [
    url(r'^', include('waves.urls.front_urls', namespace='waves')),
    url(r'^api/', include('waves.urls.api_urls', namespace='waves-api')),
    url(r'^admin/', include('waves.urls.back_urls', namespace='waves-admin')),
]
