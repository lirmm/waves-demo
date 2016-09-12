from __future__ import unicode_literals
import eav
from django.db import models
from waves.eav.config import RunnerEavConfig
from waves.models.base import DescribeAble
from django.utils.module_loading import import_string
__all__ = ['Runner', 'RunnerParam']


class Runner(DescribeAble):
    """
    Represents a generic job adaptor meta information (resolved at runtime via clazz attribute)
    """
    class Meta:
        ordering = ['name']
        db_table = 'waves_runner'
        verbose_name = 'Service runner'
        unique_together = ('name', 'clazz')

    name = models.CharField('Runner name',
                            max_length=50,
                            null=False,
                            help_text='Runner displayed name')
    available = models.BooleanField('Availability',
                                    default=True,
                                    help_text='Available for job runs')
    clazz = models.CharField('Class implementation',
                             max_length=100,
                             null=False,
                             help_text='Associated implementation class')

    def __str__(self):
        return self.name + ' [' + self.clazz + ']'

    def clean(self):
        cleaned_data = super(Runner, self).clean()
        return cleaned_data

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super(Runner, self).save(force_insert, force_update, using, update_fields)
        if len(self.runner_params.all()) == 0 and self.clazz:
            # first save, no param set, initialize them with current runners param from class
            for name, initial in self.adaptor.init_params.items():
                RunnerParam.objects.create(name=name, default=initial, runner=self)
        # Disable all related services upon change on adaptor
        if not self.available:
            for service in self.runs.all():
                service.available = False
                service.delete_runner_params()
                service.save()

    @property
    def adaptor(self):
        if self.clazz:
            job_runner = import_string(self.clazz)
            return job_runner(init_params=self.default_run_params())
        return None

    def importer(self, for_service=None):
        return self.adaptor.importer(for_service)

    def default_run_params(self):
        """
        Return a list of tuples representing current service adaptor init params
        Returns:
            List of Tuple (param_name, param_service_value, runner_param_default)
        """
        runner_params = self.runner_params.values_list('name', 'default')
        returned = dict()
        for name, default in runner_params:
            returned[name] = default
        return returned


class RunnerParam(models.Model):
    """
    Parameters used by related class object (see: waves.runners) for self initialization
    """
    class Meta:
        db_table = 'waves_runner_param'
        unique_together = ('name', 'runner')

    name = models.CharField('Name',
                            max_length=100,
                            blank=True,
                            null=True,
                            help_text='Runner init param name')
    default = models.CharField('Default',
                               max_length=50,
                               null=True,
                               blank=True,
                               help_text='Runner init param default value')
    runner = models.ForeignKey(Runner,
                               related_name='runner_params',
                               on_delete=models.CASCADE)

    def __str__(self):
        return self.name + '{defaultTxt}'.format(defaultTxt=' (def: ' + self.default + ')' if self.default else '')

    def clean(self):
        cleaned_data = super(RunnerParam, self).clean()
        if not self.default:
            self.mandatory = True
        return cleaned_data


eav.register(Runner, RunnerEavConfig)
