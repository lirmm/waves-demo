from __future__ import unicode_literals

import sys
import os
import pickle
import saga
import logging

from django.conf import settings

from waves.exceptions import JobRunException
from waves.runners.runner import JobRunner
import waves.const

__author__ = "Marc Chakiachvili <marc.chakiachvili@lirmm.fr>"

logger = logging.getLogger(__name__)


class ShellJobRunner(JobRunner):
    """
    Local script job runner, command line tools must be in path or specified as absolute path

    """
    command = None
    _environ = None
    _saga_host = 'fork://localhost'

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
            saga.job.DONE: waves.const.JOB_TERMINATED,
            saga.job.FAILED: waves.const.JOB_ERROR,
        }

    @property
    def connected(self):
        return True

    @property
    def init_params(self):
        return dict(command=self.command)

    def _connect(self):
        self._connected = True

    def _disconnect(self):
        self._connector = None
        self._connected = False

    def _prepare_job(self, job):
        try:
            _jd = dict(working_directory=job.working_dir,
                       executable=self.command,
                       arguments=job.command.get_command_line_element_list(job.job_inputs.all()),
                       output=os.path.join(job.output_dir, '.stdout'),
                       error=os.path.join(job.output_dir, '.sterr')
                       )
            with open(os.path.join(job.working_dir, 'job_description.p'), 'w+') as fp:
                pickle.dump(_jd, fp)
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
                with open(os.path.join(job.working_dir, 'job_description.p'), 'r') as fp:
                    jd_dict = pickle.load(fp)
                jd = saga.job.Description()
                for key in jd_dict.keys():
                    setattr(jd, key, jd_dict[key])
                logger.debug('JobInfo %s %s', jd, jd.__class__.__name__)
                js = saga.job.Service(self._saga_host)
                new_job = js.create_job(jd)
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
        pass

    def _job_status(self, job):
        _js = saga.job.Service(self._saga_host)
        the_job = _js.get_job(job.remote_job_id)
        return the_job.state

    def _job_results(self, job):

        pass

    def _job_run_details(self, job):
        # TODO get job run details from saga.job.attributes
        pass
