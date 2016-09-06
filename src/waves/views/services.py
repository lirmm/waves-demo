from __future__ import unicode_literals
import logging

from django.core.urlresolvers import reverse
from django.views import generic
from django.db.models import Prefetch
from django.contrib import messages

import waves.const as const

from waves.forms.services import ServiceJobForm
from waves.exceptions import JobException
from waves.models import ServiceCategory, Service
from waves.views.jobs import logger
from waves.managers.servicejobs import ServiceJobManager
from base import WavesBaseContextMixin

logger = logging.getLogger(__name__)


def get_context_meta_service(context, service):
    for meta_type, meta_label in const.SERVICE_META:
        # context['service_' + meta_type] = []
        context['service_meta_title_' + meta_type] = meta_label
    for service_meta in service.metas.all():
        meta_type = service_meta.type
        if not 'service_' + meta_type in context:
            context['service_' + meta_type] = []
        context['service_' + meta_type].append(service_meta)


class ServiceDetailView(generic.DetailView, WavesBaseContextMixin):
    model = Service
    template_name = 'services/service_details.html'
    context_object_name = 'service'
    queryset = Service.objects.all().prefetch_related("metas")
    possible_submission = False

    def get_context_data(self, **kwargs):
        context = super(ServiceDetailView, self).get_context_data(**kwargs)
        get_context_meta_service(context, self.object)
        context['categories'] = ServiceCategory.objects.all()
        return context

    def get_object(self, queryset=None):
        obj = super(ServiceDetailView, self).get_object(queryset)
        if obj.run_on and obj.run_on.available:
            self.possible_submission = True
        return obj


class CategoryDetailView(generic.DetailView, WavesBaseContextMixin, ):
    context_object_name = 'category'
    model = ServiceCategory
    template_name = 'services/category_details.html'
    context_object_name = 'category'

    def get_queryset(self):
        return ServiceCategory.objects.all().prefetch_related(
            Prefetch('category_tools',
                     queryset=Service.objects.get_public_services(user=self.request.user),
                     to_attr="category_public_tools"
                     )
        )


class CategoryListView(generic.ListView, WavesBaseContextMixin):
    template_name = "services/categories_list.html"
    model = ServiceCategory
    context_object_name = 'online_categories'

    def get_queryset(self):
        return ServiceCategory.objects.all().prefetch_related(
            Prefetch('category_tools',
                     queryset=Service.objects.get_public_services(user=self.request.user),
                     to_attr="category_public_tools"
                     )
        )


class JobSubmissionView(ServiceDetailView, generic.FormView, WavesBaseContextMixin):
    template_name = 'services/service_form.html'

    form_class = ServiceJobForm
    queryset = Service.objects.all().prefetch_related("submissions")

    def __init__(self, *args, **kwargs):
        super(JobSubmissionView, self).__init__(*args, **kwargs)
        self.job = None
        self.object = None
        self.user = None
        self.selected_submission = None

    def get_form(self, form_class=None):
        return super(JobSubmissionView, self).get_form(form_class)

    def get_context_data(self, **kwargs):
        context = super(JobSubmissionView, self).get_context_data(**kwargs)
        context['selected_submission'] = self.selected_submission
        return context

    def get(self, request, *args, **kwargs):
        self.user = self.request.user
        self.selected_submission = self.request.GET.get('submission', 'default')
        return super(JobSubmissionView, self).get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(JobSubmissionView, self).get_form_kwargs()
        extra_kwargs = {
            'submission': self.selected_submission,
            'instance': self.object,
        }
        extra_kwargs.update(kwargs)
        return extra_kwargs

    def get_success_url(self):
        return reverse('waves:job_details', kwargs={'slug': self.job.slug})

    def post(self, request, *args, **kwargs):
        self.user = self.request.user
        self.object = self.get_object()
        self.selected_submission = request.POST.get('submission', None)
        return super(JobSubmissionView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        # create job in database
        ass_email = form.cleaned_data.pop('email')
        if not ass_email and self.request.user.is_authenticated():
            ass_email = self.request.user.email
        user = self.request.user if self.request.user.is_authenticated() else None
        try:
            self.job = ServiceJobManager.create_new_job(service=self.object,
                                                        email_to=ass_email,
                                                        submitted_inputs=form.cleaned_data,
                                                        user=user)
            messages.success(
                self.request,
                "Job successfully submitted"
            )
        except JobException as e:
            logger.fatal("Create Error %s", e.message)
            messages.error(
                self.request,
                "An unexpected error occurred, sorry for the inconvenience, our team has been noticed"
            )
            return self.render_to_response(self.get_context_data(form=form))
        return super(JobSubmissionView, self).form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            "Your job could not be submitted, check errors"
        )
        return super(JobSubmissionView, self).form_invalid(form)
