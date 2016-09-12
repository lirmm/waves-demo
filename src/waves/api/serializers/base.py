from __future__ import unicode_literals

from rest_framework.serializers import ModelSerializer
from waves import utils


class WavesModelSerializer(ModelSerializer):

    @staticmethod
    def get_fully_qualified_url(url):
        # TODO replace call to get_fully_qualified with request.build_absolute_uri(url) given in Django
        return utils.get_complete_absolute_url(url)
