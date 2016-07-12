from __future__ import unicode_literals

import logging

import waves.const as const
from waves.models import Job, JobInput, JobOutput
from waves.runners import JobRunner

logger = logging.getLogger(__name__)


class MockJobRunner(JobRunner):
    """ A mock service job runner, should be used only for testing purpose
    Author : Marc Chakiachvili
    Email: marc.chakiachvili@lirmm.fr
    Date : 2015, November
    """

    def __init__(self, **kwargs):
        super(MockJobRunner, self).__init__(**kwargs)

    def _connect(self):
        self._connected = True
        return True

    def _disconnect(self):
        self._connected = False

    def _prepare_job(self, job):
        for job_input in job.inputs.values():
            # TODO parse and setup input according to their type
            logger.debug(u'current input ' + job_input.name + u'/current input value ' + job_input.value)
        for job_output in job.job_outputs.values():
            # TODO checkout output and setup associated members to their values
            logger.debug(u'current output ' + job_output.name + u'/current input value ' +
                         job_output.value)
        job.status = const.JOB_PREPARED
        job.save()

    def _run_job(self, job):
        pass

    def _cancel_job(self, job):
        pass

    def _job_status(self, job, as_text=False):
        return Job.objects.get(pk=job.pk).status

    def _job_results(self, job):
        return job.job_outputs.values()

    def _job_run_details(self, job):
        pass

    def _ready(self):
        return self._connected


