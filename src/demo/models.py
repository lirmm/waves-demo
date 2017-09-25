from __future__ import unicode_literals

from django.db import models
from waves.wcore.models import Ordered, Described
from waves.wcore.models.services import BaseService

__all__ = ['ServiceMeta', 'ServiceCategory', 'DemoWavesService']


class ServiceCategory(Ordered, Described):
    """ Service category """

    class Meta:
        ordering = ['name']
        verbose_name_plural = "Categories"
        verbose_name = "Category"

    name = models.CharField('Category Name', null=False, blank=False, max_length=255, help_text='Category name')
    ref = models.URLField('Reference', null=True, blank=True, help_text='Category online reference')
    parent = models.ForeignKey('self', null=True, blank=True, help_text='Parent category',
                               related_name='children_category', db_index=True)

    def __str__(self):
        return self.name


class DemoWavesService(BaseService):
    category = models.ForeignKey(ServiceCategory, on_delete=models.SET_NULL, null=True, related_name='category_tools')


# Create your models here.
class ServiceMeta(Ordered, Described):
    """
    Represents all meta information associated with a ATGC service service.
    Ex : website, documentation, download, related paper etc...
    """
    #: META for external website link
    META_WEBSITE = 'website'
    #: META for external documentation link
    META_DOC = 'doc'
    #: META for any download link
    META_DOWNLOAD = 'download'
    #: META for related paper view
    META_PAPER = 'paper'
    #: META for miscellaneous stuff
    META_MISC = 'misc'
    #: META to display 'cite our work'
    META_CITE = 'cite'
    #: META Service command line
    META_CMD_LINE = 'cmd'
    #: META link to user guide
    META_USER_GUIDE = 'rtfm'
    #: META features included in service
    META_FEATURES = 'feat'

    SERVICE_META = (
        (META_CITE, 'Citation'),
        (META_CMD_LINE, 'Command line'),
        (META_DOC, 'Documentation'),
        (META_DOWNLOAD, 'Downloads'),
        (META_FEATURES, 'Features'),
        (META_MISC, 'Miscellaneous'),
        (META_WEBSITE, 'Online resources'),
        (META_PAPER, 'Related Paper'),
        (META_USER_GUIDE, 'User Guide'),
    )

    class Meta:
        verbose_name = 'Service links'
        verbose_name_plural = "Service links"
        app_label = "demo"

    type = models.CharField('Meta type', max_length=100, choices=SERVICE_META)
    title = models.CharField('Title', max_length=255, blank=True, null=True)
    value = models.CharField('Link', max_length=500, blank=True, null=True)
    is_url = models.BooleanField('Is a url', editable=False, default=False)
    service = models.ForeignKey(DemoWavesService, on_delete=models.CASCADE, related_name='metas')

    def duplicate(self, service):
        """ Duplicate a Service Meta"""
        self.pk = None
        self.service = service
        self.save()
        return self

    def __str__(self):
        return '%s [%s]' % (self.title, self.type)
