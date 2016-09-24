from __future__ import unicode_literals
import logging

from django.contrib import messages
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.generic import FormView, View
from django.db import DatabaseError
from django.core.exceptions import ObjectDoesNotExist
from crispy_forms.utils import render_crispy_form
from django.core.exceptions import ValidationError
from waves.forms.admin import ImportForm
from waves.models import Service
from waves.exceptions import *

logger = logging.getLogger(__name__)


# @permission_required('services.can_edit')
class ServiceParamImportView(FormView):
    template_name = 'admin/waves/service/import/service_modal_form.html'
    form_class = ImportForm
    # success_url = '/admin/import/tools/2'
    success_message = "Data successfully imported"
    service = None
    importer = None
    tool_list = ()

    def get_context_data(self, **kwargs):
        # print 'get context'
        context = super(ServiceParamImportView, self).get_context_data(**kwargs)
        context['service_id'] = self.kwargs['service_id']
        return context

    def get_success_url(self):
        return reverse('admin:waves_service_change', args=[self.service.id])

    def form_valid(self, form):
        return super(ServiceParamImportView, self).form_valid(form)

    def form_invalid(self, form):
        return super(ServiceParamImportView, self).form_invalid(form)

    def get(self, request, *args, **kwargs):
        # print "get ", kwargs
        try:
            self.service = Service.objects.get(id=kwargs['service_id'])
            self.importer = self.service.run_on.adaptor.importer(for_service=self.service)
            # self.tool_list = self.importer.list_all_remote_services()
        except ObjectDoesNotExist:
            # We came here probably with a runner instance instead
            try:
                self.service = None
                from waves.models.runners import Runner
                runner = Runner.objects.get(id=kwargs['service_id'])
                self.importer = runner.adaptor.importer(for_runner=runner)
            except ObjectDoesNotExist as e:
                logger.info('Unable to retrieve anything, where did we come from ??? %s ', e)
                messages.error(request, message=e.message)
                return super(ServiceParamImportView, self).get(request, *args, **kwargs)
            except Exception as e:
                messages.error(request, message=e.message)
                return super(ServiceParamImportView, self).get(request, *args, **kwargs)
        try:
            self.tool_list = self.importer.list_all_remote_services()
        except RunnerException as exc:
            logger.info('Runner Exception ')
            messages.error(request, message="Connection error to remote adaptor")
        except NotImplementedError:
            logger.info('Not Implemented error')
            messages.warning(request, message='This adaptor cannot import service')
        except Exception as e:
            logger.info('Other exception %s ', e)
            messages.error(request, message=e.message)

        return super(ServiceParamImportView, self).get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(ServiceParamImportView, self).get_form_kwargs()
        extra_kwargs = {
            'tool_list': self.tool_list,
        }
        extra_kwargs.update(kwargs)
        return extra_kwargs

    def post(self, request, *args, **kwargs):
        try:
            self.service = Service.objects.get(id=kwargs['service_id'])

            logger.debug('Service %s:%s', self.service.pk, self.service)
            self.importer = self.service.run_on.adaptor.importer(for_service=self.service)
        except ObjectDoesNotExist:
            # We came here probably with a runner instance instead
            self.service = None
            from waves.models.runners import Runner
            runner = Runner.objects.get(id=kwargs['service_id'])
            self.importer = runner.adaptor.importer(for_runner=runner)
        self.tool_list = self.importer.list_all_remote_services()
        form = self.get_form()
        if request.is_ajax():
            if form.is_valid():
                logger.warning('Form is valid')
                try:
                    self.service = self.importer.import_remote_service(request.POST['tool_list'])
                    data = {
                        'url_redirect': reverse('admin:waves_service_change',
                                                args=[self.service.id])
                    }
                    messages.add_message(request, level=messages.SUCCESS, message='Parameters successfully imported')
                    redirect(reverse('admin:waves_service_change', args=[self.service.id]))
                    return JsonResponse(data, status=200)
                except Exception as e:
                    logger.error('Exception in import %s ', e)
                    form.add_error(None, ValidationError(message="Unexpected error: %s" % e))
                    form_html = render_crispy_form(form)
                    return JsonResponse({'form_html': form_html}, status=500)
            else:
                logger.warning('Form is Invalid')
                form_html = render_crispy_form(form)
                return JsonResponse({'form_html': form_html}, status=400)
        else:
            logger.error("This form is supposed to be called in ajax")


class ServiceDuplicateView(View):
    def get(self, request, *args, **kwargs):
        try:
            service = get_object_or_404(Service, id=kwargs['service_id'])
            new_service = service.duplicate()
            messages.add_message(request, level=messages.SUCCESS, message="Service successfully copied, "
                                                                          "you may edit it now")
            return redirect(reverse('admin:waves_service_change', args=[new_service.id]))
        except DatabaseError as e:
            messages.add_message(request, level=messages.WARNING, message="Error occurred during copy: %s " % e.message)
            return redirect(reverse('admin:waves_service_change', args=[kwargs['service_id']]))
