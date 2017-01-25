""" Adaptors related models super classes """
from __future__ import unicode_literals

from django.utils.module_loading import import_string
from django.db import models
from waves.utils.encrypt import Encrypt
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation

__all__ = ['DTOMixin', 'AdaptorInitParam', 'HasRunnerParamsMixin', 'HasAdaptorClazzMixin']


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
        ordering = ['name']
        verbose_name = "Initial param"
        verbose_name_plural = "Init params"

    name = models.CharField('Name', max_length=100, blank=True, null=True, help_text='Param name')
    value = models.CharField('Value', max_length=500, null=True, blank=True, help_text='Default value')
    prevent_override = models.BooleanField('Prevent override', default=False, help_text="Prevent override")
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey(for_concrete_model=False)

    def __str__(self):
        return "%s|%s" % (self.name, self.value)

    @classmethod
    def from_db(cls, db, field_names, values):
        """ Decrypt encoded value if needed for params """
        instance = super(AdaptorInitParam, cls).from_db(db, field_names, values)
        if instance.name.startswith('crypt_') and instance.value:
            instance.value = Encrypt.decrypt(instance.value)
        return instance


class HasAdaptorParamsMixin(models.Model):
    """ All class defining a 'Adaptor' should set up init parameters stored in AdaptorInitParam model """

    class Meta:
        abstract = True

    adaptor_params = GenericRelation(AdaptorInitParam)

    def set_run_params_defaults(self):
        """ Set runs params with defaults issued from concrete class object """
        object_ctype = ContentType.objects.get_for_model(self)
        for name, default in self.adaptor_defaults.items():
            defaults = {'name': name}
            if type(default) in (tuple, list, dict):
                default = default[0][0]
                defaults['prevent_override'] = True
            defaults['value'] = default
            AdaptorInitParam.objects.update_or_create(defaults=defaults, content_type=object_ctype,
                                                      object_id=self.pk, name=name)

    @property
    def run_params(self):
        """ Get defined params values from db """
        return dict(
            {name: Encrypt.decrypt(value) if name.startswith('crypt_') else value for name, value in
             self.adaptor_params.values_list('name', 'value')})


class HasAdaptorClazzMixin(HasAdaptorParamsMixin):
    """
    AdaptorClazzMixin models class has a associated concrete adaptor class element,
    where setup params wan be set in AdaptorInitParams models instance.
    :..WARNING: Adaptor class MUST have a 'init_params' property returning name/default dictionary
    """

    class Meta:
        abstract = True

    _adaptor = None
    _clazz = None
    clazz = models.CharField('Adaptor object', max_length=100, null=False,
                             help_text="This is the concrete class used to perform job execution")

    @classmethod
    def from_db(cls, db, field_names, values):
        """ Executed each time a Service is restored from DB layer"""
        instance = super(HasAdaptorClazzMixin, cls).from_db(db, field_names, values)
        instance._clazz = instance.clazz
        return instance

    def _get_concrete_adaptor(self, init_params=None):
        adaptors_params = init_params or None
        AdaptorClass = import_string(self.clazz)
        return AdaptorClass(init_params=adaptors_params)

    @property
    def has_changed_config(self):
        """ Set whether config has changed before saving """
        return self._clazz != self.clazz

    @property
    def adaptor(self):
        """ Get and returned an initialized concrete adaptor class parametrized with params defined in db
        :return: a subclass BaseAdaptor object instance
        :rtype: BaseAdaptor
        """
        if self._adaptor is None:
            if self.has_changed_config:
                self._adaptor = self._get_concrete_adaptor()
            else:
                self._adaptor = self._get_concrete_adaptor(self.run_params)
        return self._adaptor

    @adaptor.setter
    def adaptor(self, adaptor):
        """ Allow to temporarily override current adaptor instance """
        from waves.adaptors.base import BaseAdaptor
        assert (issubclass(adaptor, BaseAdaptor))
        self._adaptor = adaptor

    @property
    def adaptor_defaults(self):
        """ Retrieve init params defined associated concrete class (from clazz attribute) """
        return self._get_concrete_adaptor().init_params


class HasRunnerParamsMixin(HasAdaptorParamsMixin):
    """ Model mixin to manage params overriding and shortcut method to retrieve concrete classes """

    class Meta:
        abstract = True

    _runner = None
    runner = models.ForeignKey('Runner', related_name='%(app_label)s_%(class)s_runs', null=True, blank=False,
                               on_delete=models.SET_NULL,
                               help_text='Service job runs adapter')

    @classmethod
    def from_db(cls, db, field_names, values):
        """ Executed each time a Service is restored from DB layer"""
        # print "in base from_db"
        instance = super(HasRunnerParamsMixin, cls).from_db(db, field_names, values)
        # instance init setup loaded runner
        instance._runner = instance.runner
        return instance

    def set_run_params_defaults(self):
        """ Set runs params with defaults issued from concrete class object """
        # delete first all non runner related params setup
        print self.get_runner().adaptor_params.all()
        for runner_param in self.get_runner().adaptor_params.all():
            if runner_param.prevent_override:
                try:
                    print "prevented override ", runner_param.name
                    self.adaptor_params.get(name=runner_param.name).delete()
                    print "deleted !"
                except ObjectDoesNotExist:
                    print "Object does not exists ", runner_param.name
                    continue
                except MultipleObjectsReturned:
                    self.adaptor_params.filter(name=runner_param.name).delete()
            else:
                defaults = {'value': runner_param.value, 'prevent_override': runner_param.prevent_override}
                object_ctype = ContentType.objects.get_for_model(self)
                obj, created = AdaptorInitParam.objects.update_or_create(defaults=defaults, content_type=object_ctype,
                                                                         object_id=self.pk, name=runner_param.name)
                print "Object ", obj, "created", created

    @property
    def adaptor(self):
        """ Get and returned an initialized concrete adaptor class parametrized with params defined in db
        :return: a subclass BaseAdaptor object instance
        :rtype: BaseAdaptor
        """
        adaptor = self.get_runner().adaptor
        adaptor.init_params = self.run_params
        return adaptor

    def get_clazz(self):
        return self.runner.clazz

    @property
    def has_changed_config(self):
        return self._runner != self.runner

    @property
    def run_params(self):
        """
        Return a list of tuples representing current service adaptor init params
        :return: a Dictionary (param_name=param_service_value or runner_param_default if not set
        :rtype: dict
        """
        object_params = super(HasRunnerParamsMixin, self).run_params
        runners_default = self.get_runner().run_params
        runners_default.update(object_params)
        return object_params

    @property
    def adaptor_defaults(self):
        """ Retrieve init params defined associated concrete class (from runner attribute) """
        return self.get_runner().adaptor_defaults

    def get_runner(self):
        """ Return effective runner (could be overridden is any subclasses) """
        return self.runner
