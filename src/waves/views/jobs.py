""" WAVES jobs related web views """
from __future__ import unicode_literals

from braces.views import LoginRequiredMixin
from django.views import generic

from base import WavesBaseContextMixin
from waves.models import Job, JobOutput, JobInput
from waves.views.files import DownloadFileView


class JobView(generic.DetailView, WavesBaseContextMixin):
    """ Job Detail view """
    model = Job
    slug_field = 'slug'
    template_name = 'services/job_detail.html'
    context_object_name = 'job'


class JobListView(generic.ListView, LoginRequiredMixin, WavesBaseContextMixin):
    """ Job List view (for user) """
    model = Job
    template_name = 'services/job_list.html'
    context_object_name = 'job_list'
    paginate_by = 10

    def get_queryset(self):
        """ Retrieve user job """
        return Job.objects.get_user_job(user=self.request.user)


class JobFileView(DownloadFileView, WavesBaseContextMixin):
    """ Extended FileView for job files """
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
    """ Extended JobFileView for job outputs """
    model = JobOutput

    @property
    def file_description(self):
        return self.object.name


class JobInputView(JobFileView):
    """ Extended JobFileView for job inputs """
    model = JobInput

    @property
    def file_description(self):
        return ""
