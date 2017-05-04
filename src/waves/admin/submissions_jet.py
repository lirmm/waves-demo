from django.contrib import admin
from django.utils.safestring import mark_safe
from polymorphic.admin import PolymorphicInlineSupportMixin

from waves.admin import SubmissionOutputInline, ExitCodeInline
from waves.admin.adaptors import SubmissionRunnerParamInLine
from waves.admin.base import WavesModelAdmin, DynamicInlinesAdmin
from waves.admin.forms.services import SubmissionForm
from waves.admin.submissions import OrganizeInputInline
from waves.models import Submission
from waves.utils import url_to_edit_object


@admin.register(Submission)
class ServiceSubmissionAdmin(PolymorphicInlineSupportMixin, WavesModelAdmin, DynamicInlinesAdmin):
    """ Submission process administration -- Model Submission """
    current_obj = None
    form = SubmissionForm
    exclude = ['order']
    save_on_top = True
    list_display = ['get_name', 'service_link', 'runner_link', 'available_online', 'available_api', 'runner']
    readonly_fields = ['available_online', 'available_api']
    list_filter = (
        'service__name',
        'availability'
    )
    search_fields = ('service__name', 'label', 'override_runner__name', 'service__runner__name')
    fieldsets = [
        ('General', {
            'fields': ['service', 'name', 'availability', 'api_name', 'runner', ],
            'classes': ['collapse']
        }),
    ]
    show_full_result_count = True

    def get_model_perms(self, request):
        """
        Return empty perms dict thus hiding the model from admin index.
        """
        return {}

    def get_inlines(self, request, obj=None):
        _inlines = [
            OrganizeInputInline,
            # OrgRepeatGroupInline,
            SubmissionOutputInline,
            ExitCodeInline,
        ]
        self.inlines = _inlines
        if obj.runner is not None and obj.runner.adaptor_params.filter(prevent_override=False).count() > 0:
            self.inlines.append(SubmissionRunnerParamInLine)
        return self.inlines

    def add_view(self, request, form_url='', extra_context=None):
        context = extra_context or {}
        context['show_save_as_new'] = False
        context['show_save_and_add_another'] = False
        context['show_save'] = False
        return super(ServiceSubmissionAdmin, self).add_view(request, form_url, context)

    def get_form(self, request, obj=None, **kwargs):
        request.current_obj = obj
        form = super(ServiceSubmissionAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['runner'].widget.can_add_related = False
        form.base_fields['runner'].widget.can_change_related = False
        form.base_fields['runner'].widget.can_delete_related = False
        form.base_fields['runner'].required = False
        return form

    def get_fieldsets(self, request, obj=None):
        fieldsets = super(ServiceSubmissionAdmin, self).get_fieldsets(request, obj)
        if obj is None:  # i.e create mode
            elem = fieldsets[0][1]
            elem['classes'].append('open') if 'open' not in elem['classes'] else None
            elem['fields'].remove('available_api') if 'available_api' in elem['fields'] else None
            elem['fields'].remove('available_online') if 'available_online' in elem['fields'] else None
            elem['fields'].remove('api_name') if 'api_name' in elem['fields'] else None
        return fieldsets

    def service_link(self, obj):
        """ Back link to related service """
        return url_to_edit_object(obj.service)

    def get_name(self, obj):
        return mark_safe("<span title='Edit submission'>%s (%s)</span>" % (obj.name, obj.service))

    service_link.short_description = "Service"
    get_name.short_description = "Name"

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super(ServiceSubmissionAdmin, self).get_readonly_fields(request, obj))
        if obj is not None:
            readonly_fields.append('service')
        return readonly_fields

    def available_api(self, obj):
        return obj.available_api

    def available_online(self, obj):
        return obj.available_online

    def save_model(self, request, obj, form, change):
        if not obj.runner:
            obj.adaptor_params.all().delete()
        super(ServiceSubmissionAdmin, self).save_model(request, obj, form, change)

    def has_add_permission(self, request):
        return False

    def runner_link(self, obj):
        return url_to_edit_object(obj.get_runner())