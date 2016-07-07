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
from django.contrib import admin

import waves.views.base

# handler404 = 'waves.views.base.Template404View'
# handler500 = 'waves.views.base.Template500View'

urlpatterns = [
    url(r'^$', waves.views.base.HomePage.as_view(), name='home'),
    url(r'^about/$', waves.views.base.AboutPage.as_view(), name='about'),
    url(r'^waves/', include('waves.urls', namespace='waves')),
    url(r'^api/', include('waves.api.urls')),
    url(r'^users/', include('waves.profiles.urls', namespace='profiles')),
    url(r'^accounts/', include('waves.accounts.urls', namespace='accounts')),
    url(r'^grappelli/', include('grappelli.urls')),  # grappelli URLS
    url(r'^nested_admin/', include('nested_admin.urls')),
    url(r'^admin/', include(admin.site.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
