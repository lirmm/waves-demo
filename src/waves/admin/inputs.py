""" Submission Inputs Admin """
from __future__ import unicode_literals

from django.contrib import admin
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin, PolymorphicChildModelFilter
from waves.models.inputs import *
from django.contrib.admin.options import IS_POPUP_VAR, TO_FIELD_VAR
from django.template.response import SimpleTemplateResponse
from django.utils import six
import json

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

    def response_change(self, request, obj):
        if IS_POPUP_VAR in request.POST:
            to_field = request.POST.get(TO_FIELD_VAR)
            attr = str(to_field) if to_field else obj._meta.pk.attname
            # Retrieve the `object_id` from the resolved pattern arguments.
            value = request.resolver_match.args[0]
            new_value = obj.serializable_value(attr)
            popup_response_data = json.dumps({
                'action': 'change',
                'value': six.text_type(value),
                'obj': six.text_type(obj),
                'new_value': six.text_type(new_value),
            })
            return SimpleTemplateResponse('admin/waves/baseparam/popup_response.html', {
                'popup_response_data': popup_response_data,
            })
        return super(BaseParamAdmin, self).response_change(request, obj)



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
class AllParamModelAdmin(PolymorphicParentModelAdmin, admin.ModelAdmin):
    base_model = BaseParam
    child_models = (FileInput, ListParam, TextParam)
    list_filter = (PolymorphicChildModelFilter, 'submission', 'submission__service')
    list_display = ('get_class_label', 'name', 'submission')

    def get_class_label(self, obj):
        return obj.get_real_instance_class().class_label

    get_class_label.short_description = 'Parameter type'

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        print "in changeform_view"
        return super(AllParamModelAdmin, self).changeform_view(request, object_id, form_url, extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        print "in change view"
        return super(AllParamModelAdmin, self).change_view(request, object_id, form_url, extra_context)

    def response_change(self, request, obj):
        print "in response change"
        from django.contrib.admin.options import IS_POPUP_VAR
        if IS_POPUP_VAR in request.POST:
            print "in popup var ! almost done ?"
        return super(AllParamModelAdmin, self).response_change(request, obj)

    def response_add(self, request, obj, post_url_continue=None):
        print "in response add"
        from django.contrib.admin.options import IS_POPUP_VAR
        if IS_POPUP_VAR in request.POST:
            print "in popup var ! almost done ?"
        return super(AllParamModelAdmin, self).response_add(request, obj, post_url_continue)


