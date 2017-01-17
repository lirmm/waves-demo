""" Job Runners related models """
from __future__ import unicode_literals

from django.db import models
from waves.models.base import Described, ExportAbleMixin
from waves.models.adaptors import AdaptorInitParam, HasRunnerAdaptorParamsMixin

__all__ = ['Runner', 'RunnerInitParam']


class Runner(Described, ExportAbleMixin, HasRunnerAdaptorParamsMixin):
    """ Represents a generic job adaptor meta information (resolved at runtime via clazz attribute) """
    # TODO manage cleanly change in actual clazz value (when changed)

    class Meta:
        ordering = ['name']
        db_table = 'waves_runner'
        verbose_name = 'Execution environment'
        verbose_name_plural = "Execution environments"
    name = models.CharField('Label', max_length=50, null=False, help_text='Displayed name')
    clazz = models.CharField('Running adaptor', max_length=100, null=False)

    @property
    def runner(self):
        return self.clazz

    """@classmethod
    def from_db(cls, db, field_names, values):
        "" Executed each time a Service is restored from DB layer""
        # print "in base from_db"
        instance = super(Runner, cls).from_db(db, field_names, values)
        # instance init setup loaded runner
        instance._runner = instance.clazz
        return instance
    """

    @property
    def has_changed_runner(self):
        """
        Return true whether current object changed its runner related model
        :return: True / False
        """
        return self._runner != self.clazz

    def get_clazz(self):
        return self.clazz

    def __str__(self):
        return self.name

    @property
    def importer(self):
        """
        Shortcut function to retrieve an importer associated with a runner Model object
        :return: a Importer class instance
        """
        if self.adaptor is not None:
            return self.adaptor.importer
        else:
            raise NotImplementedError("Runner doesn't have import functionality")

    @property
    def serializer(self):
        from waves.models.serializers.runners import RunnerSerializer
        return RunnerSerializer


class RunnerInitParam(AdaptorInitParam):
    """ Parameters used by related class object (see: waves.runners) for self initialization """
    class Meta:
        proxy = True
