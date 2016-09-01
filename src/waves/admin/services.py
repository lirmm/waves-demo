from __future__ import unicode_literals

import nested_admin
from django.conf import settings
from django.contrib import admin, messages
from django.template.defaultfilters import truncatechars
from django.contrib.admin import StackedInline
from grappelli.forms import GrappelliSortableHiddenMixin
from mptt.admin import MPTTModelAdmin

import waves.const
from base import WavesTabbedModelAdmin
from waves.forms.admin.services import ServiceMetaForm, ServiceOutputForm, ServiceRunnerParamForm, ServiceForm, \
    ServiceCategoryForm, ServiceInputForm, RelatedInputForm, ServiceInputSampleForm
from waves.models import ServiceMeta, ServiceOutput, ServiceInput, RelatedInput, \
    Service, ServiceRunnerParam, ServiceCategory, Runner, ServiceExitCode, ServiceInputSample


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


class ServiceOutputInline(GrappelliSortableHiddenMixin, admin.TabularInline):
    model = ServiceOutput
    form = ServiceOutputForm
    sortable = 'order'
    extra = 0
    classes = ('grp-collapse grp-open',)
    sortable_field_name = "order"
    is_nested = False
    fields = ['name', 'from_input', 'from_input_pattern', 'short_description', 'may_be_empty', 'order']

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'from_input':
            kwargs['queryset'] = ServiceInput.objects.filter(service=request.current_obj)
        return super(ServiceOutputInline, self).formfield_for_foreignkey(db_field, request, **kwargs)


class ServiceRunnerParamInLine(admin.TabularInline):
    model = ServiceRunnerParam
    form = ServiceRunnerParamForm
    fields = ['param', 'value']
    extra = 0
    suit_classes = 'suit-tab suit-tab-runner'
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


class ServiceSampleInline(admin.TabularInline):
    model = ServiceInputSample
    form = ServiceInputSampleForm
    extra = 0
    fk_name = 'service'
    is_nested = False

    def get_field_queryset(self, db, db_field, request):
        field_queryset = super(ServiceSampleInline, self).get_field_queryset(db, db_field, request)
        if db_field.name == 'input':
            return ServiceInput.objects.filter(service=request.current_obj, type=waves.const.TYPE_FILE)
        elif db_field.name == 'dependent_input':
            return ServiceInput.objects.filter(service=request.current_obj).exclude(type=waves.const.TYPE_FILE)
        return field_queryset


class RelatedInputInline(nested_admin.NestedStackedInline, StackedInline):
    model = RelatedInput
    form = RelatedInputForm
    extra = 0
    sortable = 'order'
    fk_name = 'related_to'
    readonly_fields = ['baseinput_ptr']
    sortable_excludes = ('order', )

    def has_add_permission(self, request):
        return True


class ServiceInputInline(GrappelliSortableHiddenMixin, nested_admin.NestedStackedInline):
    model = ServiceInput
    form = ServiceInputForm
    sortable = 'order'
    extra = 0
    fk_name = 'service'
    classes = ('grp-collapse', 'grp-open')
    inlines = [RelatedInputInline, ]
    # readonly_fields = ['baseinput_ptr']
    sortable_field_name = "order"


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


class ServiceAdmin(nested_admin.NestedModelAdmin, WavesTabbedModelAdmin):

    actions = [duplicate_in_mass, mark_public]
    inlines = (
        ServiceRunnerParamInLine,
        ServiceInputInline,
        ServiceOutputInline,
        ServiceMetaInline,
        ServiceExitCodeInline,
        ServiceSampleInline,
    )
    change_form_template = 'admin/waves/service/' + WavesTabbedModelAdmin.admin_template
    form = ServiceForm
    filter_horizontal = ['restricted_client']
    readonly_fields = ['created', 'updated']
    list_display = ('name', 'api_name', 'api_on', 'version', 'run_on', 'status')
    list_filter = ('status', 'name', 'run_on')
    tab_overview = (
        (None, {
            'fields': ['category', 'name', 'status', 'run_on', 'version',
                       'short_description', 'description']
        }),
    )
    tab_details = (
        (None, {
            'fields': ['api_name', 'restricted_client', 'email_on', 'api_on', 'clazz', 'created', 'updated']
        }),
    )
    tab_runner = (ServiceRunnerParamInLine,)
    tab_inputs = (ServiceInputInline,)
    tab_outputs = (
        (None, {
            'fields': ['partial']
        }),
        ServiceOutputInline,
        ServiceExitCodeInline)
    tab_metas = (ServiceMetaInline,)
    tab_samples = (ServiceSampleInline,)
    tabs = [
        ('General', tab_overview),
        ('Details', tab_details),
        ('Metas', tab_metas),
        ('Runner Params', tab_runner),
        ('Service Inputs', tab_inputs),
        ('Services outputs', tab_outputs),
        ('Services samples', tab_samples)
    ]

    def get_form(self, request, obj=None, **kwargs):
        request.current_obj = obj
        return super(ServiceAdmin, self).get_form(request, obj, **kwargs)

    def get_formsets(self, request, obj=None):
        return super(ServiceAdmin, self).get_formsets(request, obj)

    def save_model(self, request, obj, form, change):
        super(ServiceAdmin, self).save_model(request, obj, form, change)
        if 'run_on' in form.changed_data and obj is not None:
            if obj.runner_params is not None:
                obj.runner_params.through.objects.filter(service=obj).delete()
                obj.set_default_params_4_runner(form.cleaned_data['run_on'])

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'run_on':
            kwargs['queryset'] = Runner.objects.filter(available=True)
        return super(ServiceAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class ServiceCategoryAdmin(GrappelliSortableHiddenMixin, MPTTModelAdmin):
    class Media:
        js = [
            '/static/grappelli/tinymce/jscripts/tiny_mce/tiny_mce.js',
            '/static/waves/js/tinymce.js',
        ]

    form = ServiceCategoryForm
    list_display = ('name', 'parent', 'api_name', 'short', 'ref')
    sortable_field_name = 'order'
    sortable_field_name = "order"
    mptt_indent_field = 'name'

    def short(self, obj):
        return truncatechars(obj.short_description, 100)


admin.site.register(Service, ServiceAdmin)
admin.site.register(ServiceCategory, ServiceCategoryAdmin)
