from __future__ import unicode_literals
import logging

from django.contrib import messages
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.generic import FormView, View
from django.db import DatabaseError

from waves.forms.admin import ImportForm
from waves.models import Service

logger = logging.getLogger(__name__)


# @permission_required('services.can_edit')
class ServiceParamImportView(FormView):
    template_name = 'admin/waves/service/import/service_modal_form.html'
    form_class = ImportForm
    # success_url = '/admin/import/tools/2'
    success_message = "Data successfully imported"
    service = None

    def get_context_data(self, **kwargs):
        context = super(ServiceParamImportView, self).get_context_data(**kwargs)
        context['service_id'] = self.service.id
        return context

    def get_success_url(self):
        return reverse('admin:waves_service_change', args=[self.service.id])

    def form_valid(self, form):
        return super(ServiceParamImportView, self).form_valid(form)

    def form_invalid(self, form):
        return super(ServiceParamImportView, self).form_invalid(form)

    def get(self, request, *args, **kwargs):
        try:
            self.service = Service.objects.get(id=kwargs['service_id'])
            # importer = self.service.run_on.importer()
            # self.initial = {'tool_list': importer.list_all_remote_services()}
        except NotImplementedError as e:
            logger.info('Not Implemented error')
            messages.warning(request,
                             message='This runner cannot import service')
            # self.initial = {'tool_list': (), 'service_id': kwargs['service_id']}
        except Exception as e:
            messages.add_message(request,
                                 level=messages.ERROR,
                                 message=e.message)
            # self.initial = {'tool_list': (), 'service_id': kwargs['service_id']}
        return super(ServiceParamImportView, self).get(request, *args, **kwargs)

    def get_form_kwargs(self):
        importer = self.service.run_on.importer(for_service=self.service)
        initial = {
            'tool_list': importer.list_all_remote_services(),
        }
        return initial

    def post(self, request, *args, **kwargs):
        self.service = Service.objects.get(id=kwargs['service_id'])
        logger.debug('Service %s:%s', self.service.pk, self.service)
        importer = self.service.run_on.importer(for_service=self.service)
        # self.initial = {'tool_list': importer.list_all_remote_services(),'service_id': self.service.pk}
        form = ImportForm(self.request.POST, tool_list=importer.list_all_remote_services())
        if request.is_ajax():
            if form.is_valid():
                logger.warning('Form is valid')
                try:
                    importer.import_remote_service(request.POST['tool_list'])
                    data = {
                        'url_redirect': reverse('admin:waves_service_change',
                                                args=[self.service.id])
                    }
                    messages.add_message(request, level=messages.SUCCESS, message='Parameters successfully imported')

                    return JsonResponse(data, status=200)
                except Exception as e:
                    logger.error('Exception in import ' + e.message)
                    messages.add_message(request, level=messages.ERROR, message="Error: " + e.message)
                    redirect(reverse('admin:waves_service_change', args=[self.service.id]))
            else:
                logger.warning('Form is Invalid')
                return JsonResponse(form.errors, status=400)
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

