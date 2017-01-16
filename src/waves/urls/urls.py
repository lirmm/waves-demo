from __future__ import unicode_literals

from django.conf.urls import url
from django.conf.urls import include


urlpatterns = [
    url(r'^waves/', include('waves.urls.front_urls')),
    url(r'^api/', include('waves.urls.api_urls')),
    url(r'^admin', include('waves.urls.back_urls')),
]
