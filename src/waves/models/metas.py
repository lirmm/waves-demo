""" Metas informations added to services """
from __future__ import unicode_literals

from django.db import models
import waves.const
from django.core import validators
from django.core.exceptions import ValidationError
from waves.models import Ordered, Described, Service
__all__ = ['ServiceMeta']


class ServiceMeta(Ordered, Described):
    # TODO change this into polymorphic model
    """
    Represents all meta information associated with a ATGC service service.
    Ex : website, documentation, download, related paper etc...
    """

    class Meta:
        db_table = 'waves_service_meta'
        verbose_name = 'Information'
        unique_together = ('type', 'title', 'order', 'service')

    type = models.CharField('Meta type', max_length=100, choices=waves.const.SERVICE_META)
    title = models.CharField('Title', max_length=255, blank=True, null=True)
    value = models.CharField('Link', max_length=500, blank=True, null=True)
    is_url = models.BooleanField('Is a url', editable=False, default=False)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='metas')

    def duplicate(self, service):
        """ Duplicate a Service Meta"""
        self.pk = None
        self.service = service
        self.save()
        return self

    def __str__(self):
        return '%s [%s]' % (self.title, self.type)

    def clean(self):
        try:
            validator = validators.URLValidator()
            validator(self.cleaned_data['value'])
            self.instance.is_url = True
        except ValidationError as e:
            if self.instance.type in (waves.const.META_WEBSITE, waves.const.META_DOC, waves.const.META_DOWNLOAD):
                raise e
