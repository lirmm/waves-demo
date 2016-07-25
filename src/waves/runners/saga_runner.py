from __future__ import unicode_literals

from .runner import JobRunner, JobRunException


class SagaJobRunner(JobRunner):
    """
    This class is intended to parametrize easily protocols for underlying saga services calls

    """
    _protocol = 'fork'

    @property
    def init_params(self):
        base = super(SagaJobRunner, self).init_params

    @property
    def saga_protocol(self):
        return '{}://'.format(self._protocol)

    def _run_job(self, job):
        pass

    def _prepare_job(self, job):
        pass

    def _job_status(self, job):
        pass

    def _job_run_details(self, job):
        pass

    def _job_results(self, job):
        pass

    def _disconnect(self):
        pass

    def _connect(self):
        pass

    def _cancel_job(self, job):
        pass



