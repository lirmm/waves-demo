""" Job Runners related models """
from __future__ import unicode_literals

from django.db import models
from django.utils.module_loading import import_string
from waves.importers import IMPORTERS_LIST
from waves.models.base import Described, ExportAbleMixin
from waves.models.adaptors import AdaptorInitParam, HasAdaptorClazzMixin

__all__ = ['Runner', 'RunnerInitParam']


class Runner(Described, ExportAbleMixin, HasAdaptorClazzMixin):
    """ Represents a generic job adaptor meta information (resolved at runtime via clazz attribute) """
    # TODO manage cleanly change in actual clazz value (when changed)

    class Meta:
        ordering = ['name']
        db_table = 'waves_runner'
        verbose_name = 'Execution environment'
        verbose_name_plural = "Execution environments"
    name = models.CharField('Label', max_length=50, null=False, help_text='Displayed name')
    importer_clazz = models.CharField('Importer', max_length=200, null=True, blank=True, choices=IMPORTERS_LIST)

    @property
    def importer(self):
        """
        Return an Service AdaptorImporter instance, using either
        :return: an Importer new instance
        """
        # TODO recheck importer
        if self.importer_clazz:
            importer = import_string(self.importer_clazz)
            return importer(self)
        else:
            raise None

    def __str__(self):
        return self.name

    @property
    def serializer(self):
        """ Retrieve a serializer for json export """
        from waves.models.serializers.runners import RunnerSerializer
        return RunnerSerializer

    @property
    def runs(self):
        return self.waves_service_runs.all()


class RunnerInitParam(AdaptorInitParam):
    """ Parameters used by related class object (see: waves.runners) for self initialization """
    class Meta:
        proxy = True
