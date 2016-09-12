from __future__ import unicode_literals
from eav.registry import EavConfig, Attribute


class WavesEavConfig(EavConfig):
    """
    Django-eav entity manager default configuration
    """
    manager_attr = 'eav_objects'
    manager_only = False
    # eav_attr = 'metas'
    generic_relation_attr = 'metas_values'

    @classmethod
    def get_attributes(cls):
        return Attribute.objects.all()


class JobEavConfig(WavesEavConfig):
    generic_relation_related_name = u'job_metas'

    @classmethod
    def get_attributes(cls):
        return Attribute.objects.filter(type='job')


class JobInputEavConfig(WavesEavConfig):
    generic_relation_related_name = u'input_metas'

    @classmethod
    def get_attributes(cls):
        return Attribute.objects.filter(type='job_input')


class JobOutputEavConfig(WavesEavConfig):
    generic_relation_related_name = u'output_metas'

    @classmethod
    def get_attributes(cls):
        return Attribute.objects.filter(type='job_output')


class ServiceEavConfig(WavesEavConfig):
    generic_relation_related_name = u'service_metas'

    @classmethod
    def get_attributes(cls):
        return Attribute.objects.filter(type='service')


class RunnerEavConfig(WavesEavConfig):
    generic_relation_related_name = u'runner_metas'

    @classmethod
    def get_attributes(cls):
        return Attribute.objects.filter(type='adaptor')
