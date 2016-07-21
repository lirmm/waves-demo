from __future__ import unicode_literals

import sys
import os
import pickle
import saga
import logging

from django.conf import settings

from waves.exceptions import JobRunException, RunnerConnectionError
from waves.runners.runner import JobRunner
import waves.const

__author__ = "Marc Chakiachvili <marc.chakiachvili@lirmm.fr>"

logger = logging.getLogger(__name__)


class ShellJobRunner(JobRunner):
    """
    Local script job runner, command line tools must be in path or specified as absolute path

    """
    command = None
    host = 'localhost'
    _environ = None
    _saga_protocol = 'fork'
    _connector = None

    def __init__(self, **kwargs):
        super(ShellJobRunner, self).__init__(**kwargs)
        self._environ = os.environ.copy()
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
        # current job Description
        self._jd = None
        # current job service
        # self._connector = saga.job.Service(self.saga_host)

    @property
    def saga_host(self):
        return '%s://%s' % (self._saga_protocol, self.host)

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
        self._connector = saga.job.Service(self.saga_host, session=self.session)
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
                    output=os.path.join(job.output_dir, '.stdout'),
                    error=os.path.join(job.output_dir, '.sterr')
                    )

    @property
    def init_params(self):
        return dict(command=self.command)

    def _disconnect(self):
        self._connector = None
        self._connected = False

    def _prepare_job(self, job):
        try:
            self.__dump_job_description(job, self._job_description(job))
        except pickle.PickleError as e:
            job.message = e.message
            raise e
        except IOError as e:
            job.message = e.message
            raise e
        except RuntimeError as e:
            job.message = e.message
            raise e

    def _run_job(self, job):
        """
        Launch the job with current parameters from associated history
        Args:
            job:
        """
        if os.path.isfile(os.path.join(job.working_dir, 'job_description.p')):
            try:
                jd = self.__load_job_description(job)
                logger.debug('JobInfo %s %s', jd, jd.__class__.__name__)
                new_job = self._connector.create_job(jd)
                new_job.run()
                job.remote_job_id = new_job.id
            except pickle.UnpicklingError as e:
                logger.warn('Error retrieving data from pickle %s', e.message)
                raise e
            except saga.SagaException as ex:
                logger.error("An exception occured: (%s) %s " % (ex.type, (str(ex))))
                # Trace back the exception. That can be helpful for debugging.
                logger.error(" \n*** Backtrace:\n %s" % ex.traceback)
                raise ex
        else:
            raise JobRunException('Job description  not available', job)

    def _cancel_job(self, job):
        """Jobs cannot be cancelled for Galaxy runners
        """
        the_job = self._connector.get_job(job.remote_job_id)
        try:
            the_job.cancel()
        except saga.exceptions.DoesNotExist:
            raise JobRunException('Unable to retrieve job ', job)

    def _job_status(self, job):
        try:
            the_job = self._connector.get_job(job.remote_job_id)
            return the_job.state
        except saga.exceptions.SagaException as e:
            raise JobRunException(e.message, job)

    def _job_results(self, job):
        # TODO check exit code from saga
        return True
        pass

    def _job_run_details(self, job):
        # TODO get job run details from saga.job.attributes
        pass
