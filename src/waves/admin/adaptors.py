from __future__ import unicode_literals

from django.contrib.contenttypes.admin import GenericTabularInline
from django.contrib.contenttypes.models import ContentType
from waves.admin.forms.adaptors import AdaptorInitParamForm
from waves.models import RunnerInitParam, AdaptorInitParam, SubmissionRunParam


class AdaptorInitParamInline(GenericTabularInline):
    form = AdaptorInitParamForm
    extra = 0
    fields = ['name', 'value', 'prevent_override']
    readonly_fields = ('name',)
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


class RunnerParamInline(AdaptorInitParamInline):
    """ Job Runner class instantiation parameters insertion field
    Inline are automatically generated from effective implementation class 'init_params' property """
    model = RunnerInitParam


class ServiceRunnerParamInLine(AdaptorInitParamInline):
    model = AdaptorInitParam
    fields = ['name', 'value', 'prevent_override']


class SubmissionRunnerParamInLine(AdaptorInitParamInline):
    model = AdaptorInitParam
    fields = ['name', 'value', ]

    def get_readonly_fields(self, request, obj=None):
        if obj and not obj.runner:
            self.readonly_fields = self.fields
        return super(SubmissionRunnerParamInLine, self).get_readonly_fields(request, obj)
