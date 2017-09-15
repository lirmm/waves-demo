from __future__ import unicode_literals

import swapper
from django.contrib import admin
from django.template.defaultfilters import truncatechars

from waves.wcore.admin.services import ServiceAdmin
from waves.wcore.compat import CompactInline
from .forms import ServiceMetaForm
from .models import ServiceMeta, ServiceCategory, DemoWavesService

Service = swapper.load_model("wcore", "Service")


class ServiceMetaInline(CompactInline):
    """ Waves DemoService model Admin Inline """
    model = ServiceMeta
    form = ServiceMetaForm
    exclude = ['order', ]
    extra = 0
    suit_classes = 'suit-tab suit-tab-metas'
    classes = ('grp-collapse grp-closed', 'collapse')
    fields = ['type', 'title', 'value', 'description']


class DemoServiceAdmin(ServiceAdmin):
    """ Override Waves-core Service model admin"""
    model = Service
    extra_fieldsets = [
        ('Service Category', {
            'fields': ['category']
        })
    ]

    def get_inline_instances(self, request, obj=None):
        inline_instances = super(DemoServiceAdmin, self).get_inline_instances(request, obj)
        inline_instances.append(ServiceMetaInline(self.model, self.admin_site))
        return inline_instances


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    """ Model admin for ServiceCategory model objects"""
    list_display = ('name', 'parent', 'short', 'count_serv')
    readonly_fields = ('count_serv',)
    sortable_field_name = 'order'
    fieldsets = [
        (None, {
            'fields': ['name', 'parent']
        }),
        ('Details', {
            'fields': ['short_description', 'description', 'ref']
        })
    ]

    def short(self, obj):
        """ Truncate short description in list display """
        return truncatechars(obj.short_description, 100)

    def count_serv(self, obj):
        return obj.category_tools.count()

    short.short_description = "Description"
    count_serv.short_description = "Services"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "parent" and request.current_obj is not None:
            kwargs['queryset'] = ServiceCategory.objects.exclude(id=request.current_obj.id)

        return super(ServiceCategoryAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        request.current_obj = obj
        return super(ServiceCategoryAdmin, self).get_form(request, obj, **kwargs)


admin.site.unregister(Service)
admin.site.register(DemoWavesService, DemoServiceAdmin)
