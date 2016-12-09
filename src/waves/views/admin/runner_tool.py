""" WAVES runner backoffice tools"""
from __future__ import unicode_literals

from waves.models import Runner
from django.views.generic import FormView
from django.core.exceptions import ObjectDoesNotExist
from crispy_forms.utils import render_crispy_form
from django.core.exceptions import ValidationError
from waves.exceptions import *
from waves.views.admin.export import ModelExportView
from waves.adaptors.exceptions import AdaptorConnectException
from django.conf import settings
from django.http import JsonResponse
from django.core.urlresolvers import reverse
from django.contrib import messages
from waves.forms.admin import ImportForm
import logging
from json_view import JSONDetailView
logger = logging.getLogger(__name__)


class RunnerImportToolView(FormView):
    """ Import a new service for a runner """
    template_name = 'admin/waves/import/service_modal_form.html'
    form_class = ImportForm
    # success_url = '/admin/import/tools/2'
    success_message = "Data successfully imported"
    service = None
    importer = None
    tool_list = ()
    object = None

    def get_object(self, request):
        try:
            self.object = Runner.objects.get(id=self.kwargs.get('runner_id'))
        except ObjectDoesNotExist as e:
            logger.info('Unable to retrieve anything, where did we come from ??? %s ', e)
            messages.error(request, message='Unable to retrieve runner from request')

    def get_context_data(self, **kwargs):
        context = super(FormView, self).get_context_data(**kwargs)
        return context

    def get_success_url(self):
        return reverse('admin:waves_service_change', args=[self.service.id])

    def get(self, request, *args, **kwargs):
        self.get_object(request)
        if self.object is None:
            return super(FormView, self).get(request, *args, **kwargs)
        try:
            self.tool_list = self.object.importer.list_all_remote_services()
            if len(self.tool_list) == 0:
                messages.info(request, "No tool retrieved")
        except RunnerException as exc:
            messages.error(request, message="Connection error to remote adaptor %s" % exc)
        except NotImplementedError:
            messages.error(request, message="This adaptor does not allow service import")
            if settings.DEBUG:
                raise
        except Exception as e:
            messages.error(request, message="Unexpected error %s " % e)
            if settings.DEBUG:
                raise
        return super(FormView, self).get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(FormView, self).get_form_kwargs()
        extra_kwargs = {
            'tool': self.tool_list,
        }
        extra_kwargs.update(kwargs)
        return extra_kwargs

    def remote_service_id(self, request):
        return request.POST.get('tool')

    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            self.get_object(request)
            if self.object is None:
                return super(FormView, self).get(request, *args, **kwargs)
            self.tool_list = self.object.importer.list_all_remote_services()
            form = self.get_form()
            if form.is_valid():
                logger.debug('Form is valid')
                try:
                    self.service = self.object.importer.import_remote_service(self.remote_service_id(request),
                                                                              self.object)
                    self.service.created_by = self.request.user.profile
                    self.service.category = form.cleaned_data['category']
                    self.service.save()
                    data = {
                        'url_redirect': reverse('admin:waves_service_change', args=[self.service.id])
                    }
                    messages.add_message(request, level=messages.SUCCESS, message='Parameters successfully imported')
                    return JsonResponse(data, status=200)
                except Exception as e:
                    form.add_error(None, ValidationError(message="Import Error: %s" % e))
                    form_html = render_crispy_form(form)
                    return JsonResponse({'form_html': form_html}, status=500)
            else:
                logger.warning('Form is Invalid %s', form.errors)
                form.add_error(None, ValidationError(message="Missing data"))
                form_html = render_crispy_form(form)
                return JsonResponse({'form_html': form_html}, status=400)
        else:
            logger.error("This form is supposed to be called in ajax")


class RunnerExportView(ModelExportView):
    """ Export Service representation in order to load it in another WAVES application """
    model = Runner

    @property
    def return_view(self):
        return reverse('admin:waves_runner_change', args=[self.object.id])


class RunnerTestConnectionView(JSONDetailView):
    template_name = None
    model = Runner

    def get_object(self, queryset=None):
        runner_model = super(RunnerTestConnectionView, self).get_object(queryset)
        if runner_model:
            return runner_model.adaptor
        return None

    def get_data(self, context):
        context = {'connection_result': 'Failed :'}
        try:
            self.object.connect()
            context['connection_result'] = 'Connection Success !' if self.object.connected else 'Failed :'
        except AdaptorConnectException as e:
            context['connection_result'] += 'Connection Error: <br/> %s ' % e
        return context
