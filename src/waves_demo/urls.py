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
from django.views.generic import TemplateView
from django.contrib import admin
import profiles.urls
import accounts.urls

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='home.html'), name='home'),
    url(r'^', include('demo.urls', namespace="waves_demo")),
    url(r'^waves/', include('waves.front.urls', namespace="wfront")),
    url(r'^accounts/', include('registration.backends.hmac.urls')),
    url(r'^about$', TemplateView.as_view(template_name='about.html'), name='about'),
    url(r'^rest$', TemplateView.as_view(template_name='rest/rest_api.html'), name='rest_services'),
    url(r'^wcore', include('waves.wcore.urls', namespace='wcore')),
    url(r'^waves/api', include('waves.wcore.api.urls', namespace='wapi')),
    url(r'^user/', include(profiles.urls, namespace='profiles')),
    url(r'^jet/', include('jet.urls', 'jet')),  # Django JET URLS
    url(r'^jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),  # Django JET dashboard URLS
    url(r'^admin/', include(admin.site.urls)),
    url(r'^users/', include(accounts.urls, namespace='accounts')),
]

if settings.DEBUG is True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
                   + static(settings.STATIC_URL,
                            document_root=settings.STATIC_ROOT)
