from __future__ import unicode_literals
import logging

from django.views.generic import View
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.contrib import messages

from waves.models import Job

logger = logging.getLogger(__name__)


class JobCancelView(View):

    def get(self, request, *args, **kwargs):
        try:
            job = get_object_or_404(Job, id=kwargs['job_id'])
            runner = job.adaptor
            runner.cancel_job(job)
            messages.add_message(request, level=messages.SUCCESS, message="Job successfully cancelled")
            return redirect(reverse('admin:waves_job_change', args=[job.id]))
        except Exception as e:
            messages.add_message(request, level=messages.WARNING, message="Error occurred: %s " % e.message)
            return redirect(reverse('admin:waves_job_change', args=[kwargs['job_id']]))
