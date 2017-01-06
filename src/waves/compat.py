""" Compatility file to enable dependents apps behaviour """
from __future__ import unicode_literals
from django.conf import settings

if 'tabbed_admin' not in settings.INSTALLED_APPS:
    from django.contrib.admin import ModelAdmin

    class WavesModelAdmin(ModelAdmin):
        """ Tabbed faked model admin """
        admin_template = 'change_form.html'
else:
    from tabbed_admin import TabbedModelAdmin

    class WavesModelAdmin(TabbedModelAdmin):
        """ Override TabbedModelAdmin admin_template """
        admin_template = 'tabbed_change_form.html'

if 'jet' not in settings.INSTALLED_APPS:
    from django.contrib.admin import StackedInline

    class CompactInline(StackedInline):
        """ Inherit base class"""
        pass
else:
    from jet.admin import CompactInline

if 'bootstrap_themes' not in settings.INSTALLED_APPS:
    def list_themes():
        return ()
else:
    from bootstrap_themes import list_themes


if 'ckeditor' not in settings.INSTALLED_APPS:
    from django.db import models

    class RichTextField(models.TextField):
        """ Override RicheTextField """
        pass
else:
    from ckeditor.fields import RichTextField
