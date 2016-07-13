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

    def get_file_name(self):
        return self.object.value

    def get_file_path(self):
        return self.object.file_path


class JobOutputView(JobFileView):
    model = JobOutput


class JobInputView(JobFileView):
    model = JobInput
