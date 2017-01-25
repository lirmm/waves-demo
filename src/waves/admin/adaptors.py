from __future__ import unicode_literals

from django.contrib.contenttypes.admin import GenericTabularInline
from django.contrib.contenttypes.models import ContentType
from waves.admin.forms.adaptors import AdaptorInitParamForm
from waves.models import RunnerInitParam, AdaptorInitParam, SubmissionRunParam


class AdaptorInitParamInline(GenericTabularInline):
    form = AdaptorInitParamForm
    extra = 0
    fields = ['get_name', 'value', 'prevent_override']
    readonly_fields = ('get_name',)
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

    def get_name(self, obj):
        if obj.name.startswith('crypt_'):
            return obj.name.replace('crypt_', '')
        return obj.name


class RunnerParamInline(AdaptorInitParamInline):
    """ Job Runner class instantiation parameters insertion field
    Inline are automatically generated from effective implementation class 'init_params' property """
    model = RunnerInitParam


class ServiceRunnerParamInLine(AdaptorInitParamInline):
    model = AdaptorInitParam
    fields = ['get_name', 'value']


class SubmissionRunnerParamInLine(AdaptorInitParamInline):
    model = AdaptorInitParam
    fields = ['get_name', 'value', ]

    def get_queryset(self, request):
        print request.current_obj
        if request.current_obj.runner:
            object_ctype = ContentType.objects.get_for_model(request.current_obj)
            print "ctype1", object_ctype.pk
            print super(SubmissionRunnerParamInLine, self).get_queryset(request)
            return super(SubmissionRunnerParamInLine, self).get_queryset(request)
        else:
            object_ctype = ContentType.objects.get_for_model(request.current_obj.service)
            print "ctype2", object_ctype.pk
            print AdaptorInitParam.objects.filter(content_type=object_ctype,
                                                  object_id=request.current_obj.service.pk,
                                                  )
            return AdaptorInitParam.objects.filter(content_type=object_ctype,
                                                   object_id=request.current_obj.service.pk)


    def get_readonly_fields(self, request, obj=None):
        if not obj.runner:
            self.readonly_fields = self.fields
        return super(SubmissionRunnerParamInLine, self).get_readonly_fields(request, obj)
