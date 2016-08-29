from __future__ import unicode_literals
from rest_framework import serializers
from .services import ServiceSerializer
from waves.models import ServiceCategory, Service
import waves.const as const


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    """
    Service category serializer/unserializer
    """

    class Meta:
        model = ServiceCategory
        fields = ('url', 'name', 'short_description', 'tools')
        lookup_field = 'name'
        extra_kwargs = {
            'url': {'view_name': 'waves:waves-services-category-detail', 'lookup_field': 'name'}
        }
        depth = 1

    tools = serializers.SerializerMethodField('get_active_tools')

    def get_active_tools(self, category):
        tool_queryset = Service.objects.filter(category=category,
                                               status=const.SRV_PUBLIC)
        serializer = ServiceSerializer(instance=tool_queryset,
                                       many=True,
                                       context=self.context,
                                       fields=('url', 'name', 'short_description', 'version'))
        return serializer.data
