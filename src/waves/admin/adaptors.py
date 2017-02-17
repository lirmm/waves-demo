from __future__ import unicode_literals

from django.contrib.contenttypes.admin import GenericTabularInline

from waves.admin.forms.adaptors import AdaptorInitParamForm
from waves.models import AdaptorInitParam


class AdaptorInitParamInline(GenericTabularInline):
    form = AdaptorInitParamForm
    model = AdaptorInitParam
    extra = 0
    fields = ['name', 'value', 'default_value', 'prevent_override']
    readonly_fields = ('name', 'default_value')
    classes = ('collapse grp-collapse grp-closed',)
    suit_classes = 'suit-tab suit-tab-adaptor'
    can_delete = False
    verbose_name = 'Execution param'
    verbose_name_plural = "Execution parameters"

    def has_delete_permission(self, request, obj=None):
        """ No delete permission for runners params
        :return: False
        """
        return False

    def has_add_permission(self, request):
        """ No add permission for runners params
        :return: False
        """
        return False

    def default_value(self, obj):
        """ Get default values from related adaptor concrete class instance """
        if obj.crypt:
            init_value = obj.content_object.adaptor_defaults['crypt_%s' % obj.name]
            if init_value is not None:
                return "*" * len(init_value) if init_value is not None else '-'
        else:
            init_value = obj.content_object.adaptor_defaults[obj.name]
        if hasattr(init_value, '__iter__'):
            return 'list'
        return init_value if init_value is not None else '-'


class RunnerParamInline(AdaptorInitParamInline):
    """ Job Runner class instantiation parameters insertion field
    Inline are automatically generated from effective implementation class 'init_params' property """
    model = AdaptorInitParam


class ServiceRunnerParamInLine(AdaptorInitParamInline):
    """ Adaptors parameters for Service """
    model = AdaptorInitParam


class SubmissionRunnerParamInLine(AdaptorInitParamInline):
    """ Adaptors parameters for submission when overridden """
    model = AdaptorInitParam
    fields = ['name', 'value', ]

    def get_readonly_fields(self, request, obj=None):
        if obj and not obj.runner:
            self.readonly_fields = self.fields
        return super(SubmissionRunnerParamInLine, self).get_readonly_fields(request, obj)
