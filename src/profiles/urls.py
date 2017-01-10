""" WAVES user accounts urls """
from __future__ import unicode_literals

from django.conf.urls import url
from .views import EditProfile, ShowProfile

urlpatterns = [
    url(r'^me/$', ShowProfile.as_view(), name='show_self'),
    url(r'^edit$', EditProfile.as_view(), name='edit_self'),
    url(r'^(?P<slug>[\w\-]+)$', ShowProfile.as_view(), name='show'),
]
