from __future__ import unicode_literals
from django.conf.urls import url
import waves.views.profiles

urlpatterns = [
    url(r'^me$', waves.views.profiles.ShowProfile.as_view(), name='show_self'),
    url(r'^me/edit$', waves.views.profiles.EditProfile.as_view(), name='edit_self'),
    url(r'^(?P<slug>[\w\-]+)$', waves.views.profiles.ShowProfile.as_view(),
        name='show'),
]
