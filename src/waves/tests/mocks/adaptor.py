""" Mock Adaptor class for tests purpose
"""
from __future__ import unicode_literals

from waves.adaptors.base import BaseAdaptor
import waves.adaptors.const as jobconst
# TODO implements missing methods
import random, string


class MockConnector(object):
    pass


class MockJobRunnerAdaptor(BaseAdaptor):
    def _job_status(self, job):
        # time.sleep()
        if job.status == jobconst.JOB_RUNNING:
            # print "job is running, set it to completed!"
            return jobconst.JOB_COMPLETED
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
            jobconst.JOB_UNDEFINED: jobconst.JOB_UNDEFINED,
            jobconst.JOB_CREATED: jobconst.JOB_CREATED,
            jobconst.JOB_QUEUED: jobconst.JOB_QUEUED,
            jobconst.JOB_RUNNING: jobconst.JOB_RUNNING,
            jobconst.JOB_SUSPENDED: jobconst.JOB_SUSPENDED,
            jobconst.JOB_CANCELLED: jobconst.JOB_CANCELLED,
            jobconst.JOB_COMPLETED: jobconst.JOB_COMPLETED,
            jobconst.JOB_TERMINATED: jobconst.JOB_TERMINATED,
            jobconst.JOB_ERROR: jobconst.JOB_ERROR,
        }
