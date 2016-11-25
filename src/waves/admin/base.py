""" Base class for WAVES models.Admin """
from __future__ import unicode_literals

from django.conf import settings
from django.contrib import admin, messages
from django.core.urlresolvers import reverse
from django.shortcuts import redirect

if 'tabbed_admin' in settings.INSTALLED_APPS:
    from tabbed_admin import TabbedModelAdmin


    class WavesTabbedModelAdmin(TabbedModelAdmin):
        """ Override TabbedModelAdmin admin_template """

        class Media:
            css = {
                'screen': ('waves/css/tabbed_admin.css',)
            }
            js = ('waves/admin/services.js',)

        admin_template = 'tabbed_change_form.html'

        @property
        def media(self):
            # Overrides media class to skip first parent media import
            media = super(admin.ModelAdmin, self).media
            return media
else:
    class WavesTabbedModelAdmin(admin.ModelAdmin):
        """ Tabbed faked model admin """

        class Media:
            js = ('waves/admin/services.js',)

        admin_template = 'change_form.html'


def duplicate_in_mass(modeladmin, request, queryset):
    from django.contrib import messages
    for obj in queryset.all():
        try:
            new = obj.duplicate()
            messages.add_message(request, level=messages.SUCCESS, message="Object %s successfully duplicated" % obj)
        except StandardError as e:
            messages.add_message(request, level=messages.ERROR, message="Object %s error %s " % (obj, e.message))
    if queryset.count() == 1:
        return redirect(
            reverse('admin:%s_%s_change' % (new._meta.app_label, new._meta.model_name), args=[new.id]))


def export_in_mass(modeladmin, request, queryset):
    """ Allow multiple models objects (inheriting from ExportAbleMixin) to be exported
     at the same time """
    for obj in queryset.all():
        try:
            file_path = obj.serialize()
            messages.add_message(request, level=messages.SUCCESS,
                                 message="Object exported successfully to %s " % file_path)
        except StandardError as e:
            messages.add_message(request, level=messages.ERROR, message="Object export %s error %s " % (obj, e.message))


def mark_public_in_mass(modeladmin, request, queryset):
    """ Allow status 'public' to be set in mass for objects implementing 'publish' method """
    for obj in queryset.all():
        try:
            obj.publishUnPublish()
            messages.add_message(request, level=messages.SUCCESS, message="Object %s successfully published" % obj)
        except StandardError as e:
            messages.add_message(request, level=messages.ERROR, message="Object %s error %s " % (obj, e.message))


class ExportInMassMixin(admin.ModelAdmin):
    """ modelAdmin mixin, add to actions 'export_in_mass' to export models to disk """

    def get_actions(self, request):
        """ Add action 'export_in_mass' """
        actions = super(ExportInMassMixin, self).get_actions(request)
        actions['export_in_mass'] = (export_in_mass, 'export_in_mass', "Export selected to disk")
        return actions


class DuplicateInMassMixin(admin.ModelAdmin):
    """ modelAdmin mixin, add to actions 'duplicate_in_mass' to export models to disk """

    def get_actions(self, request):
        """ Add action 'duplicate_in_mass' """
        actions = super(DuplicateInMassMixin, self).get_actions(request)
        actions['duplicate_in_mass'] = (duplicate_in_mass, 'duplicate_in_mass', "Duplicate selected")
        return actions


class MarkPublicInMassMixin(admin.ModelAdmin):
    """ modelAdmin mixin, add to actions 'duplicate_in_mass' to export models to disk """

    def get_actions(self, request):
        """ Add action 'duplicate_in_mass' """
        actions = super(MarkPublicInMassMixin, self).get_actions(request)
        actions['mark_public_in_mass'] = (mark_public_in_mass, 'mark_public_in_mass', "Publish/Un-publish selected")
        return actions
