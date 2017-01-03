""" Job Runners related models """
from __future__ import unicode_literals

from django.db import models
from django.utils.module_loading import import_string

from waves.models.base import DescribeAble, ExportAbleMixin, AdaptorInitParam
from waves.models.managers.runners import RunnerManager, RunnerParamManager

__all__ = ['Runner', 'RunnerParam']


class Runner(DescribeAble, ExportAbleMixin):
    """ Represents a generic job adaptor meta information (resolved at runtime via clazz attribute) """
    class Meta:
        ordering = ['name']
        db_table = 'waves_runner'
        verbose_name = 'Runner'
    #: private attribute to set if clazz have been modified before save
    _clazz = None
    objects = RunnerManager()
    name = models.CharField('Runner label', max_length=50, null=False, help_text='Displayed name')
    clazz = models.CharField('Adaptor', max_length=100, null=False)

    def __str__(self):
        return self.name

    @classmethod
    def from_db(cls, db, field_names, values):
        """
        Update _clazz attribute on model object loading from db
        :param db:
        :param field_names:
        :param values:
        :return:
        """
        instance = super(Runner, cls).from_db(db, field_names, values)
        instance._clazz = instance.clazz
        return instance

    @property
    def adaptor(self):
        """
        Import and create a new instance of Runner related class implementation
        :return: An waves.adaptors.* instance or None if no class specified
        """
        if self.clazz:
            Adaptor = import_string(self.clazz)
            return Adaptor(init_params=self.default_run_params())
        return None

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

    def default_run_params(self):
        """
        Return a list of tuples representing current service adaptor init params

        :return: a dictionary (param_name=runner_param_default)
        :rtype: dict
        """
        from waves.utils.encrypt import Encrypt
        runner_params = self.runner_params.values_list('name', 'value')
        returned = dict()
        for name, default in runner_params:
            if name.startswith('crypt_') and default:
                returned[name] = Encrypt.decrypt(default)
            else:
                returned[name] = default
        return returned

    @property
    def has_changed_clazz(self):
        """
        Return True if current object has changed clazz before save
        :return: True / False
        """
        return self._clazz != self.clazz

    @property
    def serializer(self):
        from waves.models.serializers.runners import RunnerSerializer
        return RunnerSerializer


class RunnerParam(AdaptorInitParam):
    """ Parameters used by related class object (see: waves.runners) for self initialization """
    class Meta:
        db_table = 'waves_runner_run_param'
        unique_together = ('name', 'runner')
    objects = RunnerParamManager()
    runner = models.ForeignKey(Runner, related_name='runner_params', on_delete=models.CASCADE)

