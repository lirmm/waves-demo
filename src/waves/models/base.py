from __future__ import unicode_literals
import uuid
from django.db import models
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
    """Time stamped 'able' models objects, add fields to inherited objects

    .. note::
        This class add also default ordering by -updated, -created (reverse order)
    """
    class Meta:
        abstract = True
        ordering = ['-updated', '-created']
    #: (auto_now_add): set when model object is created
    created = models.DateTimeField('Created on', auto_now_add=True, editable=False, help_text='Creation timestamp')
    #: (auto_now): set each time model object is saved in database
    updated = models.DateTimeField('Last Update', auto_now=True, editable=False, help_text='Last update timestamp')


class OrderAble(models.Model):
    """ Order-able models objects,

    .. note::
        Default ordering is set to 'order'
    """
    class Meta:
        abstract = True
        ordering = ['order']
    #: positive integer field (default to 0)
    order = models.PositiveIntegerField(default=0)


class DescribeAble(models.Model):
    """ A model object which inherit from this class add two description fields to model objects
    """
    class Meta:
        abstract = True
    #: Text field to set up a complete description of model object, with HTML editor enabled
    description = RichTextField('Description', null=True, blank=True, help_text='Full description (HTML enabled)')
    #: text field for short version, no html
    short_description = models.TextField('Short Description', null=True, blank=True,
                                         help_text='Short description (Text only)')


class SlugAble(models.Model):
    """ Add a 'slug' field to models Objects, based on uuid.uuid4 field generator, this field is mainly used for models
    objects urls
    """
    class Meta:
        abstract = True
    #: UUID field is base on uuid4 generator.
    slug = models.UUIDField(default=uuid.uuid4, blank=True, editable=False)


class ApiAble(models.Model):
    """ An API-able model object need a 'api_name', in order to setup dedicated url for this model object
    """
    class Meta:
        abstract = True
    #: A char field, must be unique for a model instance
    api_name = models.CharField(max_length=100, null=True, blank=True, help_text='Api short code, must be unique')


class UrlMixin(object):
    """ Url Miwin allow easy generation or absolute url related to any model object

    .. note::
       Sub-classes must define a get_absolute_url() method > See
       `Django get_absolute_url <https://docs.djangoproject.com/en/1.9/ref/models/instances/#get-absolute-url>`_
    """
    def get_url(self):
        """ Calculate and return absolute 'front-office' url for a model object
        :return: unicode the absolute url
        """
        path = self.get_absolute_url()
        protocol = getattr(settings, "PROTOCOL", "http")
        domain = Site.objects.get_current().domain
        port = getattr(settings, "PORT", "")
        if port:
            assert port.startswith(":"), "The PORT setting must have a preceeding ':'."
        return "%s://%s%s%s" % (protocol, domain, port, path)

    def get_url_path(self):
        """ Return relative url path
        :return: unicode the relative url
        """
        import urlparse
        try:
            url = self.get_url()
        except NotImplemented:
            raise
        bits = urlparse.urlparse(url)
        return urlparse.urlunparse(('', '') + bits[2:])
