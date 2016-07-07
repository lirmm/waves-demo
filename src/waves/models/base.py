from __future__ import unicode_literals
from django.db import models
import uuid


class TimeStampable(models.Model):
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
    class Meta:
        abstract = True
        ordering = ['order']

    order = models.PositiveIntegerField(default=0)


class DescribeAble(models.Model):
    class Meta:
        abstract = True

    description = models.TextField('Description',
                                   null=True,
                                   blank=True,
                                   help_text='Full description (HTML enabled)')
    short_description = models.TextField('Short Description',
                                         null=True,
                                         blank=True,
                                         help_text='Short description (Text only)')


class SlugAble(models.Model):
    class Meta:
        abstract = True

    slug = models.UUIDField(default=uuid.uuid1,
                            blank=True,
                            editable=False)
