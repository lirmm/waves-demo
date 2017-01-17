""" Adaptors related models super classes """
from __future__ import unicode_literals

from django.db import models
from waves.utils.encrypt import Encrypt
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation

__all__ = ['DTOMixin', 'AdaptorInitParam', 'HasRunnerAdaptorParamsMixin']


class DTOMixin(object):
    """ Some models (Service / Inputs / Outputs / ExitCodes / Jobs) need to be able to be loaded from Adaptors
    """

    def from_dto(self, dto):
        """ Copy attributes from dto to current object, do not override current objects attributes with no
        correspondence """
        for var in dir(dto):
            if not var.startswith('_'):
                setattr(self, var, getattr(dto, var))

    def to_dto(self, dto):
        # TODO check if really needed
        """ Copy object attributes to a DTO """
        for var in dir(self):
            if not var.startswith('_'):
                setattr(dto, var, getattr(self, var))


class AdaptorInitParam(models.Model):
    """ Base Class For adaptor initialization params """

    class Meta:
        # abstract = True
        verbose_name = "Initial param"
        verbose_name_plural = "Init params"

    name = models.CharField('Name', max_length=100, blank=True, null=True, help_text='Param name')
    value = models.CharField('Value', max_length=500, null=True, blank=True, help_text='Default value')
    prevent_override = models.BooleanField('Prevent override', help_text="Prevent override")
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey(for_concrete_model=False)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.name.startswith('crypt_'):
            self.value = Encrypt.encrypt(self.value)
        super(AdaptorInitParam, self).save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return "%s|%s" % (self.name, self.value)

    @classmethod
    def from_db(cls, db, field_names, values):
        """ Decrypt encoded value if needed for params """
        instance = super(AdaptorInitParam, cls).from_db(db, field_names, values)
        if instance.name.startswith('crypt_') and instance.value:
            instance.value = Encrypt.decrypt(instance.value)
        return instance


class HasRunnerAdaptorParamsMixin(models.Model):
    """ Model mixin class to gather behaviour attached to 'Adaptor Runs params' relationship """

    class Meta:
        abstract = True

    _runner = None
    _adaptor = None
    adaptor_params = GenericRelation(AdaptorInitParam)

    def save(self, *args, **kwargs):
        super(HasRunnerAdaptorParamsMixin, self).save(*args, **kwargs)

    def reset_run_params(self):
        """ Reset runner params to default, if a param with same name exists, should not delete """
        # retrieve related params in table
        self.adaptor_params.exclude(name__in=self.adaptor.init_params.keys()).delete()
        for param in self.adaptor_params.filter(prevent_override=True):
            # for param in self.related_mngr.filter(prevent_override=True):
            AdaptorInitParam.objects.update_or_create(defaults={'value': param.value,
                                                                'prevent_override': True},
                                                      name=param.name, content_type=param.content_type,
                                                      object_id=param.object_id)

    @classmethod
    def from_db(cls, db, field_names, values):
        """ Executed each time a Service is restored from DB layer"""
        # print "in base from_db"
        instance = super(HasRunnerAdaptorParamsMixin, cls).from_db(db, field_names, values)
        # instance init setup loaded runner
        instance._runner = instance.runner
        return instance

    @property
    def has_changed_runner(self):
        """
        Return true whether current object changed its runner related model
        :return: True / False
        """
        print "from db has_change_runner ", (self._runner != self.runner)
        print self._runner
        print self.runner
        return self._runner != self.runner

    @property
    def run_params(self):
        """
        Return a list of tuples representing current service adaptor init params
        :return: a Dictionary (param_name=param_service_value or runner_param_default if not set
        :rtype: dict
        """
        return dict(
            {name: Encrypt.decrypt(value) if name.startswith('crypt_') else value for name, value in
             self.adaptor_params.values_list('name', 'value')})

    @property
    def adaptor(self):
        """ Return current adaptor for Service
        :return: a BaseAdaptor instance
        """
        if self._adaptor is None:
            # try load it from clazz name
            from django.utils.module_loading import import_string
            Adaptor = import_string(self.get_clazz())
            self._adaptor = Adaptor(init_params=self.run_params)
        return self._adaptor

    def get_clazz(self):
        return self.runner.clazz

    @adaptor.setter
    def adaptor(self, adaptor):
        """ Allow to temporarily override current adaptor instance"""
        from waves.adaptors.base import BaseAdaptor
        assert (issubclass(adaptor, BaseAdaptor))
        self._adaptor = adaptor
