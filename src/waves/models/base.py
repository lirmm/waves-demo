from __future__ import unicode_literals
import uuid
from django.db import models
from django.utils.html import strip_tags
from django.contrib.sites.models import Site

from django.conf import settings
if 'ckeditor' not in settings.INSTALLED_APPS:
    class RichTextField(models.TextField):
        pass
else:
    # If ckeditor enabled, use RichTextField, if not, define simply TextField subclass
    from ckeditor.fields import RichTextField

__all__ = ['TimeStampable', 'OrderAble', 'DescribeAble', 'SlugAble', 'ApiAble', 'UrlMixin']


class TimeStampable(models.Model):
    """
    Time stamped models objects, add :
    - "created" (auto_now_add)
    - "updated" (auto_now)
    fields to Models objects
    """

    class Meta:
        abstract = True
        ordering = ['-updated', '-created']

    created = models.DateTimeField('Created on',
                                   auto_now_add=True,
                                   editable=False,
                                   help_text='Creation timestamp')
    updated = models.DateTimeField('Last Update',
                                   auto_now=True,
                                   editable=False,
                                   help_text='Last update timestamp')


class OrderAble(models.Model):
    """
    Order-able models objects, ordered with "order" field (Positive Integer default 0)
    """

    class Meta:
        abstract = True
        ordering = ['order']

    order = models.PositiveIntegerField(default=0)


class DescribeAble(models.Model):
    """
    Add description and short_description field to models Objects
    - Description will accept

    """

    class Meta:
        abstract = True

    description = RichTextField('Description',
                                null=True,
                                blank=True,
                                help_text='Full description (HTML enabled)')
    short_description = models.TextField('Short Description',
                                         null=True,
                                         blank=True,
                                         help_text='Short description (Text only)')


class SlugAble(models.Model):
    """
    Add a 'slug' field to models Objects, based on uuid.uuid1 field generator
    """

    class Meta:
        abstract = True

    slug = models.UUIDField(default=uuid.uuid4,
                            blank=True,
                            editable=False)


class ApiAble(models.Model):
    class Meta:
        abstract = True

    api_name = models.CharField(max_length=100, null=True, blank=True,
                                help_text='Api short code, must be unique')


class UrlMixin(object):
    def get_url(self):
        path = self.get_absolute_url()
        protocol = getattr(settings, "PROTOCOL", "http")
        domain = Site.objects.get_current().domain
        port = getattr(settings, "PORT", "")
        if port:
            assert port.startswith(":"), "The PORT setting must have a preceeding ':'."
        return "%s://%s%s%s" % (protocol, domain, port, path)

    def get_url_path(self):
        import urlparse
        try:
            url = self.get_url()
        except NotImplemented:
            raise
        bits = urlparse.urlparse(url)
        return urlparse.urlunparse(('', '') + bits[2:])
