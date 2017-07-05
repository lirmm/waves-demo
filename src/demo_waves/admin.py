from django.contrib import admin
from django.template.defaultfilters import truncatechars
# Register your models here.
from waves.compat import CompactInline

from .forms import ServiceMetaForm
from .models import ServiceMeta


class ServiceMetaInline(CompactInline):
    model = ServiceMeta
    form = ServiceMetaForm
    exclude = ['order', ]
    extra = 0
    suit_classes = 'suit-tab suit-tab-metas'
    classes = ('grp-collapse grp-closed', 'collapse')
    fields = ['type', 'title', 'value', 'description']

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    """ Model admin for ServiceCategory model objects"""
    list_display = ('name', 'parent', 'api_name', 'short', 'count_serv')
    readonly_fields = ('count_serv',)
    sortable_field_name = 'order'
    fieldsets = [
        (None, {
            'fields': ['name', 'parent', 'api_name']
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


