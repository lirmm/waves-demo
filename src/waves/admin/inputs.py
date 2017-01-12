""" Submission Inputs Admin """
from __future__ import unicode_literals

from django.contrib import admin
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin, PolymorphicChildModelFilter
from waves.models.inputs import *
__all__ = ['AllParamModelAdmin']


class BaseParamAdmin(PolymorphicChildModelAdmin):
    """ Base Input admin """
    base_model = BaseParam
    exclude = ['order']
    base_fieldsets = (
        ('General', {
            'fields': ('label', 'name', 'default', 'required', 'submission'),
            'classes': []
        }),
        ('Details', {
            'fields': ('cmd_format', 'help_text', 'edam_formats', 'edam_datas', 'multiple'),
            'classes': ['collapse']
        }),
        ('Dependencies', {
            'fields': ('related_to', 'when_value', 'repeat_group'),
            'classes': ['collapse']
        }),
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if request.current_obj:
            if db_field.name == 'repeat_group':
                kwargs['queryset'] = RepeatedGroup.objects.filter(submission=request.current_obj.submission)
            elif db_field.name == "related_to":
                kwargs['queryset'] = BaseParam.objects.filter(submission=request.current_obj.submission)
        return super(BaseParamAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        request.current_obj = obj
        return super(BaseParamAdmin, self).get_form(request, obj, **kwargs)


@admin.register(FileInput)
class FileInputAdmin(BaseParamAdmin):
    base_model = FileInput
    # fields = ('allowed_extensions', 'max_size')
    # show_in_index = True
    extra_fieldset_title = 'File params'


@admin.register(TextParam)
class TextParamAdmin(BaseParamAdmin):
    base_model = TextParam


@admin.register(BooleanParam)
class BooleanParamAdmin(BaseParamAdmin):
    base_model = BooleanParam
    extra_fieldset_title = 'Boolean params'


@admin.register(ListParam)
class ListParamAdmin(BaseParamAdmin):
    base_model = ListParam
    # show_in_index = False
    # fields = ('list_mode', 'list_elements')
    extra_fieldset_title = 'List params'


@admin.register(BaseParam)
class AllParamModelAdmin(PolymorphicParentModelAdmin):
    base_model = BaseParam
    child_models = (FileInput, ListParam, TextParam)
    list_filter = (PolymorphicChildModelFilter, 'submission', 'submission__service')
    list_display = ('get_class_label', 'name', 'submission')

    def get_class_label(self, obj):
        return obj.get_real_concrete_instance_class().class_label

    get_class_label.short_description = 'Parameter type'
