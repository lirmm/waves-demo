""" Compatibility file to enable dependents apps behaviour """
from __future__ import unicode_literals
from django.conf import settings


try:
    if 'jet' in settings.INSTALLED_APPS:
        from jet.admin import CompactInline
    else:
        raise ImportError
except ImportError:
    from django.contrib.admin import StackedInline

    class CompactInline(StackedInline):
        """ Inherit base class """
        pass

try:
    if 'ckeditor' in settings.INSTALLED_APPS:
        from ckeditor.fields import RichTextField
    else:
        raise ImportError
except ImportError:
    from django.db import models

    class RichTextField(models.TextField):
        """ Override RichTextField """
        pass
