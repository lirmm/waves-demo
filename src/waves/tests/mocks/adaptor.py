""" Mock Adaptor class for tests purpose
"""
from __future__ import unicode_literals

from waves.adaptors.base import JobRunnerAdaptor
import waves.const
# TODO implements missing methods
import random, string


class MockConnector(object):
    pass


class MockJobRunnerAdaptor(JobRunnerAdaptor):
    def _job_status(self, job):
        # time.sleep()
        if job.status == waves.const.JOB_RUNNING:
            # print "job is running, set it to completed!"
            return waves.const.JOB_COMPLETED
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
            waves.const.JOB_UNDEFINED: waves.const.JOB_UNDEFINED,
            waves.const.JOB_CREATED: waves.const.JOB_CREATED,
            waves.const.JOB_QUEUED: waves.const.JOB_QUEUED,
            waves.const.JOB_RUNNING: waves.const.JOB_RUNNING,
            waves.const.JOB_SUSPENDED: waves.const.JOB_SUSPENDED,
            waves.const.JOB_CANCELLED: waves.const.JOB_CANCELLED,
            waves.const.JOB_COMPLETED: waves.const.JOB_COMPLETED,
            waves.const.JOB_TERMINATED: waves.const.JOB_TERMINATED,
            waves.const.JOB_ERROR: waves.const.JOB_ERROR,
        }
