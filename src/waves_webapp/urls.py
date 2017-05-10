"""waves_services URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from waves.views.base import *
from django.contrib import admin

urlpatterns = [
    url(r'^$', HomePage.as_view(), name='home'),
    url(r'^waves/', include('waves.urls.urls', namespace='waves')),
    url(r'^waves/api/v1/', include('waves.api.v1.urls', namespace='waves_api_v1')),
    url(r'^waves/api/v2/', include('waves.api.v2.urls', namespace='waves_api')),
    # url(r'^accounts/', include('accounts.urls', namespace='account')),
    # url(r'^profiles/', include('profiles.urls', namespace='profile')),
    url(r'^jet/', include('jet.urls', 'jet')),  # Django JET URLS
    url(r'^jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),  # Django JET dashboard URLS
    # url(r'^chaining/', include('smart_selects.urls')),
    url(r'^admin/', include(admin.site.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
              + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
