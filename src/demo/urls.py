from __future__ import unicode_literals

from django.conf.urls import url
from .views import CategoryListView, CategoryDetailView, ServiceDetailView


urlpatterns = [
    url(r'^categories/$', CategoryListView.as_view(), name='categories_list'),
    url(r'^category/(?P<pk>[0-9]+)/$', CategoryDetailView.as_view(), name='category_details'),
    # url(r'^service/(?P<pk>[0-9]+)/', ServiceDetailView.as_view())
]
