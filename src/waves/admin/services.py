from __future__ import unicode_literals

import nested_admin

from django.conf import settings
from django.contrib import admin, messages
from django.template.defaultfilters import truncatechars
from django.contrib.admin import StackedInline
from grappelli.forms import GrappelliSortableHiddenMixin
from mptt.admin import MPTTModelAdmin
from django.forms.models import BaseInlineFormSet
from django.core.exceptions import ObjectDoesNotExist, ValidationError

import waves.const
from base import WavesTabbedModelAdmin
from waves.forms.admin.services import *
from waves.models.services import *
from waves.models.runners import Runner
from waves.models.samples import *


class ServiceMetaInline(GrappelliSortableHiddenMixin, admin.TabularInline):
    model = ServiceMeta
    form = ServiceMetaForm
    sortable = 'order'
    extra = 1
    suit_classes = 'suit-tab suit-tab-metas'
    classes = ('grp-collapse grp-open',)
    fields = ['type', 'title', 'value', 'description', 'order']
    sortable_field_name = "order"
    is_nested = False


class ServiceOutputFromInputFormset(BaseInlineFormSet):
    def clean(self):
        try:
            forms = [f for f in self.forms
                     if f.cleaned_data
                     and not f.cleaned_data.get('DELETE', False)]
            # print "cleandformset ", self.instance.srv_input, ", mandatory ", self.instance.srv_input.mandatory, ', default ', self.instance.srv_input.default
            if self.instance.file_pattern and self.instance.from_input:
                if len(forms) < self.instance.service.submissions.count():
                    raise ValidationError('You must setup an value for all possible submission')
                elif len(forms) < self.instance.service.submissions.count():
                    raise ValidationError('You can not provide more origin than possible submissions')
                else:
                    f_submission = set(f.instance.submission for f in forms)
                    s_submission = set(s for s in self.instance.service.submissions.all())
                    if not f_submission.__eq__(s_submission):
                        raise ValidationError('Misconfiguration for origins, check your data')
        except AttributeError:
            pass


class ServiceOutputFromInputInline(nested_admin.NestedTabularInline):
    model = ServiceOutputFromInputSubmission
    form = ServiceOutputFromInputSubmissionForm
    formset = ServiceOutputFromInputFormset
    fields = ['submission', 'srv_input', ]
    fk_name = 'srv_output'
    verbose_name = "Valuated from"
    verbose_name_plural = "Output is valuated from an input"
    extra = 2

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'submission' and request.current_obj is not None:
            kwargs['queryset'] = ServiceSubmission.objects.filter(service=request.current_obj)
        return super(ServiceOutputFromInputInline, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def get_extra(self, request, obj=None, **kwargs):
        if obj is not None:
            return int(obj.service.submissions.count() - obj.from_input_submission.count())
        else:
            if request.current_obj:
                return request.current_obj.submissions.count()
        # By default we return only one extra (setup with only one available submission form)
        return 1


class ServiceOutputInline(GrappelliSortableHiddenMixin, nested_admin.NestedStackedInline, admin.TabularInline):
    model = ServiceOutput
    form = ServiceOutputForm
    sortable = 'order'
    extra = 0
    classes = ('grp-collapse grp-open',)
    sortable_field_name = "order"
    fk_name = 'service'
    fields = ['name', 'from_input', 'file_pattern', 'short_description', 'may_be_empty', 'order']
    verbose_name_plural = "Service outputs"
    inlines = [ServiceOutputFromInputInline, ]

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'from_input' and request.current_obj is not None:
            kwargs['queryset'] = BaseInput.objects.filter(service=request.current_obj.default_submission,
                                                          mandatory=True)
        return super(ServiceOutputInline, self).formfield_for_foreignkey(db_field, request, **kwargs)


class ServiceRunnerParamInLine(admin.TabularInline):
    model = ServiceRunnerParam
    form = ServiceRunnerParamForm
    fields = ['param', 'value']
    extra = 0
    suit_classes = 'suit-tab suit-tab-adaptor'
    can_delete = False
    readonly_fields = ['param']
    is_nested = False

    def get_max_num(self, request, obj=None, **kwargs):
        if obj is not None:
            return len(obj.runner_params.all())
        else:
            return 0

    def get_min_num(self, request, obj=None, **kwargs):
        if obj is not None:
            return len(obj.runner_params.all())
        else:
            return 0

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return request.current_obj is not None


class ServiceSampleDependentInputInline(GrappelliSortableHiddenMixin, admin.TabularInline):
    model = ServiceSampleDependentsInput
    fk_name = 'sample'
    extra = 0
    sortable_field_name = "order"


class ServiceSampleInline(nested_admin.NestedTabularInline):
    model = ServiceInputSample
    form = ServiceInputSampleForm
    extra = 0
    fk_name = 'service'
    is_nested = False
    verbose_name_plural = "Service sample ('input' apply only to 'default' submission params)"
    inlines = [
        ServiceSampleDependentInputInline
    ]

    def get_field_queryset(self, db, db_field, request):
        field_queryset = super(ServiceSampleInline, self).get_field_queryset(db, db_field, request)
        if request.current_obj is not None:
            if db_field.name == 'input':
                return ServiceInput.objects.filter(service=request.current_obj.default_submission, type=waves.const.TYPE_FILE)
            elif db_field.name == 'dependent_input':
                return ServiceInput.objects.filter(service=request.current_obj.default_submission).exclude(type=waves.const.TYPE_FILE)
        return field_queryset


class RelatedInputInline(nested_admin.NestedStackedInline, StackedInline):
    model = RelatedInput
    form = RelatedInputForm
    extra = 0
    sortable = 'order'
    fk_name = 'related_to'
    readonly_fields = ['baseinput_ptr']
    sortable_excludes = ('order',)
    verbose_name = 'Related Input'
    verbose_name_plural = "Related Inputs"

    def has_add_permission(self, request):
        return True


class ServiceInputInline(GrappelliSortableHiddenMixin, nested_admin.NestedStackedInline):
    # TODO use new PolymorphicInlines classes provided with django-polymorphic 1.0
    # from polymorphic.admin import PolymorphicInlineSupportMixin, StackedPolymorphicInline
    model = ServiceInput
    form = ServiceInputForm
    sortable = 'order'
    extra = 0
    fk_name = 'service'
    classes = ('grp-collapse', 'grp-open')
    inlines = [RelatedInputInline, ]
    sortable_field_name = "order"
    verbose_name = 'Input'
    verbose_name_plural = "Inputs"

    def get_queryset(self, request):
        qs = super(ServiceInputInline, self).get_queryset(request)
        return qs.instance_of(ServiceInput)


class ServiceExitCodeInline(admin.TabularInline):
    model = ServiceExitCode
    extra = 1
    fk_name = 'service'
    is_nested = False
    classes = ('grp-collapse', 'grp-open')


def duplicate_in_mass(modeladmin, request, queryset):
    from django.contrib import messages
    for srv in queryset.all():
        try:
            srv.duplicate()
            messages.add_message(request, level=messages.SUCCESS, message="Service %s successfully duplicated" % srv)
        except StandardError as e:
            messages.add_message(request, level=messages.ERROR, message="Service %s error %s " % (srv, e.message))


def mark_public(modeladmin, request, queryset):
    for srv in queryset.all():
        try:
            srv.status = waves.const.SRV_PUBLIC
            srv.save()
            messages.add_message(request, level=messages.SUCCESS, message="Service %s successfully updated" % srv)
        except StandardError as e:
            messages.add_message(request, level=messages.ERROR, message="Service %s error %s " % (srv, e.message))


duplicate_in_mass.short_description = "Duplicate selected services"
mark_public.short_description = "Mark Services as Public"


class ServiceSubmissionInline(GrappelliSortableHiddenMixin, nested_admin.NestedStackedInline):
    model = ServiceSubmission
    form = ServiceSubmissionForm
    extra = 0
    fk_name = 'service'
    sortable = 'order'
    sortable_field_name = "order"
    classes = ('grp-collapse', 'grp-open')
    fields = ['label', 'default', 'available_online', 'available_api', 'api_name', 'created', 'updated', "order"]
    readonly_fields = ['created', 'updated']
    inlines = [ServiceInputInline, ]


class ServiceAdmin(nested_admin.NestedModelAdmin, WavesTabbedModelAdmin):
    actions = [duplicate_in_mass, mark_public]
    inlines = (
        ServiceRunnerParamInLine,
        ServiceSubmissionInline,
        # ServiceInputInline,
        ServiceOutputInline,
        ServiceMetaInline,
        ServiceExitCodeInline,
        ServiceSampleInline,
    )
    change_form_template = 'admin/waves/service/' + WavesTabbedModelAdmin.admin_template
    form = ServiceForm
    filter_horizontal = ['restricted_client']
    readonly_fields = ['created', 'updated']
    list_display = ('name', 'api_name', 'api_on', 'web_on', 'version', 'run_on', 'status', 'created_by')
    list_filter = ('status', 'name', 'run_on')
    tab_overview = (
        (None, {
            'fields': ['category', 'name', 'status', 'run_on', 'version',
                       'short_description', 'description']
        }),
    )
    tab_details = (
        (None, {
            'fields': ['api_name', 'created_by', 'restricted_client', 'email_on', 'api_on', 'web_on', 'created',
                       'updated']
            # TODO reintegrate 'clazz'
        }),
    )
    tab_runner = (ServiceRunnerParamInLine,)
    # tab_inputs = (ServiceInputInline,)
    tab_submission = (ServiceSubmissionInline, )
    tab_outputs = (
        # (None, {
        #     'fields': ['partial']
        # }),
        ServiceOutputInline,
        ServiceExitCodeInline)
    tab_metas = (ServiceMetaInline,)
    tab_samples = (ServiceSampleInline,)
    tabs = [
        ('General', tab_overview),
        ('Details', tab_details),
        ('Metas', tab_metas),
        ('Run configuration', tab_runner),
        # ('Service Inputs', tab_inputs),
        ('Submissions', tab_submission),
        ('Outputs', tab_outputs),
        ('Samples', tab_samples)
    ]

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super(ServiceAdmin, self).get_readonly_fields(request, obj)
        if not request.user.is_superuser:
            readonly_fields.append('created_by')
        if obj is not None and obj.created_by != request.user.profile:
            readonly_fields.append('api_name')
            readonly_fields.append('clazz')
            readonly_fields.append('version')
        return readonly_fields

    def get_form(self, request, obj=None, **kwargs):
        request.current_obj = obj
        form = super(ServiceAdmin, self).get_form(request, obj, **kwargs)
        form.current_user = request.user
        return form

    def get_formsets(self, request, obj=None):
        return super(ServiceAdmin, self).get_formsets(request, obj)

    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user.profile
        super(ServiceAdmin, self).save_model(request, obj, form, change)
        if 'run_on' in form.changed_data and obj is not None:
            if obj.runner_params is not None:
                obj.runner_params.through.objects.filter(service=obj).delete()
                obj.set_default_params_4_runner(form.cleaned_data['run_on'])
        if obj.submissions.count() == 0:
            obj.create_default_submission()

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'run_on':
            kwargs['queryset'] = Runner.objects.filter(available=True)
        return super(ServiceAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class ServiceCategoryAdmin(GrappelliSortableHiddenMixin, MPTTModelAdmin):
    form = ServiceCategoryForm
    list_display = ('name', 'parent', 'api_name', 'short', 'ref')
    sortable_field_name = 'order'
    sortable_field_name = "order"
    mptt_indent_field = 'name'

    def short(self, obj):
        return truncatechars(obj.short_description, 100)


admin.site.register(Service, ServiceAdmin)
admin.site.register(ServiceCategory, ServiceCategoryAdmin)
