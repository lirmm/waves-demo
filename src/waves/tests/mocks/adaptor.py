""" Mock Adaptor class for tests purpose
"""
from __future__ import unicode_literals

import random
import string

import waves_adaptors.const
from waves_adaptors.core.base import JobAdaptor


class MockConnector(object):
    pass


class MockJobRunnerAdaptor(JobAdaptor):
    def _job_status(self, job):
        # time.sleep()
        if job.status == waves_adaptors.const.JOB_RUNNING:
            return waves_adaptors.const.JOB_COMPLETED
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
            waves_adaptors.const.JOB_UNDEFINED: waves_adaptors.const.JOB_UNDEFINED,
            waves_adaptors.const.JOB_CREATED: waves_adaptors.const.JOB_CREATED,
            waves_adaptors.const.JOB_QUEUED: waves_adaptors.const.JOB_QUEUED,
            waves_adaptors.const.JOB_RUNNING: waves_adaptors.const.JOB_RUNNING,
            waves_adaptors.const.JOB_SUSPENDED: waves_adaptors.const.JOB_SUSPENDED,
            waves_adaptors.const.JOB_CANCELLED: waves_adaptors.const.JOB_CANCELLED,
            waves_adaptors.const.JOB_COMPLETED: waves_adaptors.const.JOB_COMPLETED,
            waves_adaptors.const.JOB_TERMINATED: waves_adaptors.const.JOB_TERMINATED,
            waves_adaptors.const.JOB_ERROR: waves_adaptors.const.JOB_ERROR,
        }
