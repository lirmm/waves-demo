""" Mock Adaptor class for tests purpose
"""
from __future__ import unicode_literals

import random
import string

import waves.adaptors.const
from waves.adaptors.core.base import JobAdaptor


class MockConnector(object):
    pass


class MockJobRunnerAdaptor(JobAdaptor):
    def _job_status(self, job):
        # time.sleep()
        if job.status == waves.adaptors.const.JOB_RUNNING:
            return waves.adaptors.const.JOB_COMPLETED
        return job.next_status

    def _run_job(self, job):
        job.remote_job_id = '%s-%s' % (job.id, ''.join(random.sample(string.letters, 15)))
        pass

    def _disconnect(self):
        self._connector = None
        pass

    def _connect(self):
        self._connector = MockConnector()
        self._connected = True
        pass

    def _job_results(self, job):
        return True

    def _job_run_details(self, job):
        pass

    def _prepare_job(self, job):
        pass

    def _cancel_job(self, job):
        pass

    def __init__(self, init_params={}, **kwargs):
        super(MockJobRunnerAdaptor, self).__init__(init_params, **kwargs)
        self._states_map = {
            waves.adaptors.const.JOB_UNDEFINED: waves.adaptors.const.JOB_UNDEFINED,
            waves.adaptors.const.JOB_CREATED: waves.adaptors.const.JOB_CREATED,
            waves.adaptors.const.JOB_QUEUED: waves.adaptors.const.JOB_QUEUED,
            waves.adaptors.const.JOB_RUNNING: waves.adaptors.const.JOB_RUNNING,
            waves.adaptors.const.JOB_SUSPENDED: waves.adaptors.const.JOB_SUSPENDED,
            waves.adaptors.const.JOB_CANCELLED: waves.adaptors.const.JOB_CANCELLED,
            waves.adaptors.const.JOB_COMPLETED: waves.adaptors.const.JOB_COMPLETED,
            waves.adaptors.const.JOB_TERMINATED: waves.adaptors.const.JOB_TERMINATED,
            waves.adaptors.const.JOB_ERROR: waves.adaptors.const.JOB_ERROR,
        }
