from __future__ import unicode_literals

import saga
import os

import pickle
import logging

from waves.adaptors.runner import JobRunnerAdaptor
import waves.const

__author__ = "Marc Chakiachvili <marc.chakiachvili@lirmm.fr>"

logger = logging.getLogger(__name__)


class ShellJobAdaptor(JobRunnerAdaptor):
    """
    Local script job adaptor, command line tools must be in path or specified as absolute path

    """
    command = None
    host = 'localhost'
    _environ = None
    _protocol = 'fork'
    _connector = None

    def __init__(self, **kwargs):
        super(ShellJobAdaptor, self).__init__(**kwargs)
        self._environ = os.environ.copy()
        # current job Description
        self._jd = None
        # current job service
        # self._connector = saga.job.Service(self.saga_host)
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
        return '%s://%s' % (self._protocol, self.host)

    @property
    def session(self):
        session = saga.Session()
        if self.context:
            session.add_context(self.context)
        return session

    @property
    def context(self):
        return None

    def _connect(self):
        self._connector = saga.job.Service(str(self.saga_host), session=self.session)
        self._connected = self._connector is not None

    def __load_job_description(self, job):
        with open(os.path.join(job.working_dir, 'job_description.p'), 'r') as fp:
            jd_dict = pickle.load(fp)
        self._jd = saga.job.Description()
        for key in jd_dict.keys():
            setattr(self._jd, key, jd_dict[key])
        return self._jd

    def __dump_job_description(self, job, job_description):
        with open(os.path.join(job.working_dir, 'job_description.p'), 'w+') as fp:
            pickle.dump(job_description, fp)

    def _job_description(self, job):
        return dict(working_directory=job.working_dir,
                    executable=self.command,
                    arguments=job.command.get_command_line_element_list(job.job_inputs.all()),
                    output=os.path.join(job.output_dir, job.stdout),
                    error=os.path.join(job.output_dir, job.stderr)
                    )

    @property
    def init_params(self):
        return dict(command=self.command, host=self.host)

    def _disconnect(self):
        self._connector.close()
        self._connector = None
        self._connected = False

    def _prepare_job(self, job):
        self.__dump_job_description(job, self._job_description(job))

    def _run_job(self, job):
        """
        Launch the job with current parameters from associated history
        Args:
            job:
        """
        jd = self.__load_job_description(job)
        logger.debug('JobInfo %s %s', jd, jd.__class__.__name__)
        new_job = self._connector.create_job(jd)
        new_job.run()
        job.remote_job_id = new_job.id

    def _cancel_job(self, job):
        """
        Jobs Cancel if connector is available
        """
        try:
            the_job = self._connector.get_job(str(job.remote_job_id))
            the_job.cancel()
        except saga.SagaException as exc:
            logger.warning('Remote cancel job error:\n%s: %s' % (exc.__class__.__name__, str(exc)))

    def _job_status(self, job):
        try:
            the_job = self._connector.get_job(str(job.remote_job_id))
            return the_job.state
        except saga.SagaException as exc:
            logger.warning('Remote job status error:\n%s: %s' % (exc.__class__.__name__, str(exc)))
            return waves.const.JOB_UNDEFINED

    def _job_results(self, job):
        # TODO check exit code from saga
        return True
        pass

    def _job_run_details(self, job):
        # TODO get job run details from saga.job.attributes
        pass
