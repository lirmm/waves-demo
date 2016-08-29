from __future__ import unicode_literals

from django.conf.urls import url
from django.conf.urls import include
from waves.views.base import *

urlpatterns = [
    url(r'^$', HomePage.as_view(), name='home'),
    url(r'^accounts/', include('waves.urls.accounts_url')),
    url(r'^api/', include('waves.urls.api_urls')),
    url(r'^admin/', include('waves.urls.back_urls')),
    url(r'^waves/', include('waves.urls.front_urls'))
]