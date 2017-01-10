"""WAVES models export module for Services """
from __future__ import unicode_literals

import waves.settings
from django.db import transaction
from rest_framework import serializers
from waves.models import Runner, RunnerParam
from . import RelatedSerializerMixin


class RunnerParamSerializer(serializers.ModelSerializer):
    class Meta:
        model = RunnerParam
        fields = ('name', 'value', 'prevent_override')


class RunnerSerializer(serializers.ModelSerializer, RelatedSerializerMixin):
    class Meta:
        model = Runner
        fields = ('name', 'clazz', 'runner_params')

    runner_params = RunnerParamSerializer(many=True)

    @transaction.atomic
    def create(self, validated_data):
        runner_params = validated_data.pop('runner_params')
        runner = Runner.objects.create(**validated_data)
        runner.runner_run_params.all().delete()
        runner.runner_run_params = self.create_related(foreign={'runner': runner},
                                                       serializer=RunnerParamSerializer,
                                                       datas=runner_params)
        return runner
