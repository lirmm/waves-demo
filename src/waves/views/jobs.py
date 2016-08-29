from __future__ import unicode_literals

import logging

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import generic

from waves.models import Job, JobOutput, JobInput
from waves.views.files import DownloadFileView

logger = logging.getLogger(__name__)


class JobView(generic.DetailView):
    model = Job
    slug_field = 'slug'
    template_name = 'services/job_detail.html'
    context_object_name = 'job'

    def dispatch(self, request, *args, **kwargs):
        return super(JobView, self).dispatch(request, *args, **kwargs)


class JobListView(generic.ListView):
    model = Job
    template_name = 'services/job_list.html'
    context_object_name = 'job_list'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(JobListView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Job.objects.get_user_job(user=self.request.user)


class JobFileView(DownloadFileView):
    context_object_name = "file_obj"

    @property
    def file_name(self):
        return self.object.value

    @property
    def file_path(self):
        return self.object.file_path

    @property
    def return_link(self):
        return self.object.job.get_absolute_url()


class JobOutputView(JobFileView):
    model = JobOutput

    @property
    def file_description(self):
        return self.object.srv_output.short_description if self.object.srv_output else self.object.value


class JobInputView(JobFileView):
    model = JobInput

    @property
    def file_name(self):
        return self.object.srv_input.label if self.object.srv_input else self.object.value

    @property
    def file_description(self):
        return self.object.srv_input.short_description if self.object.srv_input else self.object.value
