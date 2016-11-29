from __future__ import unicode_literals
import os

import waves.const
import logging
import saga

from waves.adaptors.exceptions import AdaptorConnectException, AdaptorJobException
from waves.adaptors.base import JobRunnerAdaptor

logger = logging.getLogger(__name__)

__group__ = 'Local'


class ShellJobAdaptor(JobRunnerAdaptor):
    """
    Local script job adaptor, command line tools must be in path or specified as absolute path

    """
    name = "Local job script adaptor"
    #: Host on where to launch job
    host = 'localhost'
    #: Saga-python protocol scheme
    protocol = 'fork'

    def __init__(self, **kwargs):
        super(ShellJobAdaptor, self).__init__(**kwargs)
        self._states_map = {
            saga.job.UNKNOWN: waves.const.JOB_UNDEFINED,
            saga.job.NEW: waves.const.JOB_CREATED,
            saga.job.PENDING: waves.const.JOB_QUEUED,
            saga.job.RUNNING: waves.const.JOB_RUNNING,
            saga.job.SUSPENDED: waves.const.JOB_SUSPENDED,
            saga.job.CANCELED: waves.const.JOB_CANCELLED,
            saga.job.DONE: waves.const.JOB_COMPLETED,
            saga.job.FAILED: waves.const.JOB_ERROR,
        }

    @property
    def saga_host(self):
        """ Construct Saga-python adaptor uri scheme """
        return '%s://%s' % (self.protocol, self.host)

    @property
    def session(self):
        """ Configuration of Saga-python session (with context) for adaptor """
        session = saga.Session()
        if self.context:
            session.add_context(self.context)
        return session

    @property
    def context(self):
        """ Create / initialize Saga-python session context """
        return None

    def _connect(self):
        try:
            self._connector = saga.job.Service(str(self.saga_host), session=self.session)
            self._connected = self._connector is not None
        except saga.SagaException as exc:
            raise AdaptorConnectException(msg=exc.message)

    def _job_description(self, job):
        return dict(working_directory=job.working_dir,
                    executable=self.command,
                    arguments=job.command.get_command_line_element_list(job.job_inputs.all()),
                    output=os.path.join(job.working_dir, job.stdout),
                    error=os.path.join(job.working_dir, job.stderr)
                    )

    @property
    def init_params(self):
        """ Saga-python adaptor base init params """
        return dict(command=self.command)

    def _disconnect(self):
        self._connector.close()
        self._connector = None
        self._connected = False

    def _prepare_job(self, job):
        # Nothing to do here
        pass

    def _run_job(self, job):
        """
        Launch the job with current parameters from associated history
        Args:
            job:
        """
        try:
            jd_dict = self._job_description(job)
            jd = saga.job.Description()
            for key in jd_dict.keys():
                setattr(jd, key, jd_dict[key])
            new_job = self._connector.create_job(jd)
            new_job.run()
            job.remote_job_id = new_job.id
        except saga.SagaException as exc:
            raise AdaptorJobException(exc)

    def _cancel_job(self, job):
        """
        Jobs Cancel if connector is available
        """
        try:
            the_job = self._connector.get_job(str(job.remote_job_id))
            the_job.cancel()
        except saga.SagaException as exc:
            raise AdaptorJobException(exc)

    def _job_status(self, job):
        try:
            the_job = self._connector.get_job(str(job.remote_job_id))
            return the_job.state
        except saga.SagaException as exc:
            raise AdaptorJobException(exc)

    def _job_results(self, job):
        try:
            saga_job = self._connector.get_job(str(job.remote_job_id))
            logger.debug('Job Exit Code %s', saga_job.exit_code)
            job.results_available = (saga_job.state == saga.job.DONE)
            job.exit_code = saga_job.exit_code
        except saga.SagaException as exc:
            raise AdaptorJobException(exc)

    def _job_run_details(self, job):
        remote_job = self._connector.get_job(str(job.remote_job_id))
        details = waves.const.JobRunDetails(job.id, str(job.slug), remote_job.id, remote_job.name,
                                            remote_job.exit_code,
                                            remote_job.created, remote_job.started, remote_job.finished,
                                            remote_job.execution_hosts)
        logger.debug('Job Exit Code %s %s', remote_job.exit_code, remote_job.finished)
        return details