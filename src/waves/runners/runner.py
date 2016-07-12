from __future__ import unicode_literals

import logging

from django.db import transaction
from django.conf import settings

import waves.const
from waves.exceptions import *
from waves.models import Job, JobInput, JobOutput

logger = logging.getLogger(__name__)


class JobRunner(object):
    """
    Abstract JobRunner class, declare expected behaviour from any Waves's JobRunner
    """
    _connector = None
    _parser = None
    _type_map = {}
    _states_map = {}
    _state_allow_cancel = (waves.const.STATUS_LIST[1:5])

    def __init__(self, init_params={}, **kwargs):
        """
        Initialize a runner
        :return: a new JobRunner object

        """
        self._initialized = False
        self._connected = False
        self._connector = kwargs['connector'] if 'connector' in kwargs else None
        self._parser = kwargs['parser'] if 'parser' in kwargs else None
        try:
            for name, value in init_params.items():
                getattr(self, name)
                setattr(self, name, value)
        except AttributeError as e:
            raise RunnerUnexpectedInitParam('Unexpected init param %s ' % e)
        self._initialized = all(self.init_params)

    @property
    def init_params(self):
        return dict()

    def importer_clazz(self, service=None):
        """
        Get a service importer from this runner
        Returns:
            ToolRunnerImporter
        """
        from waves.runners.importer import ToolRunnerImporter
        return ToolRunnerImporter(self, service)

    @property
    def connected(self):
        return self._connector is not None and self._connected is True

    def connect(self):
        """Connect to runner
        :return: _connector reference or raise an ConnectionException
        """
        if self.connected:
            return self._connector
        else:
            logger.info('Try re-connect')
            try:
                self._connect()
            except Exception as exc:
                logger.fatal(self.dump_config())
                self._connected = False
                raise RunnerConnectionError(str(exc), 'Connect')
            finally:
                # TODO code needed here ?
                pass
        return self._connector

    def disconnect(self):
        """
        Shut down connection to runner. Called after job runner execution to disconnect from remote
        :return: boolean or raise an ConnectionException
        """
        if not self.connected:
            # if not connected, do nothing
            return
        try:
            self._disconnect()
            self._connector = None
            self._connected = False
            return
        except Exception as exc:
            logger.fatal(self.dump_config())
            raise RunnerConnectionError(str(exc), 'Disconnect')

    def prepare_job(self, job):
        """
        Command execution preparation process
        Args:
            job:
        """
        if not self._ready():
            raise RunnerNotReady()
        if job.status != waves.const.JOB_CREATED:
            raise JobInconsistentStateError(job.get_status_display(), waves.const.STR_JOB_CREATED)
        try:
            if not self.connected:
                self.connect()
            self._prepare_job(job)
            job.status = waves.const.JOB_PREPARED
            logger.info('Job %s prepared', job.slug)
        except Exception as exc:
            job.status = waves.const.JOB_ERROR
            raise JobPrepareException('Prepare error:[%s] %s' %
                                      (exc.__class__.__name__, str(exc)))
        finally:
            job.save()
        return True

    def run_job(self, job):
        assert isinstance(job, Job)
        if job.status != waves.const.JOB_PREPARED:
            raise JobInconsistentStateError(job.get_status_display(), waves.const.STR_JOB_PREPARED)
        try:
            if not self.connected:
                self.connect()
            if not self._ready():
                raise RunnerNotReady()
            self._run_job(job)
            job.status = waves.const.JOB_QUEUED
            logger.info('Job %s queued', job.slug)
        except Exception as exc:
            job.status = waves.const.JOB_ERROR
            raise JobRunException('Run job error: %s: %s' %
                                  (exc.__class__.__name__, str(exc)))
        finally:
            job.save()
        return job.remote_job_id

    def cancel_job(self, job):
        """
        Cancel a running job on runner class
        :param job:
        :return:
        """
        if job.status not in dict(self._state_allow_cancel):
            raise JobInconsistentStateError(job.get_status_display(), self._state_allow_cancel, 'Cancel not allowed')
        try:
            self._cancel_job(job)
            job.status = waves.const.JOB_CANCELLED
            logger.info('Job %s cancelled ', job.slug)
        except Exception as exc:
            logger.warn('Cancel job %s not applied to runner %s', job.pk, job.service.run_on)
            job.message = 'Could not cancel job'
            raise JobRunException('Cancel job error:\n%s: %s' %
                                  (exc.__class__.__name__, str(exc)))
        finally:
            job.save()
        return job.status

    def job_status(self, job):
        """
        Return current Job status
        :param job:
        :param as_text:
        :return:
        """
        assert isinstance(job, Job)
        try:
            if not self.connected:
                self.connect()
            if not self._ready():
                raise RunnerNotReady('%s runner not ready : \nInit_param:%s\nConnector:%s - initialized:%s' % (
                    self.__class__.__name__, self.init_params, self._connector, self._initialized))
            job.status = self.__map_status(self._job_status(job))
        except Exception as exc:
            job.status = waves.const.JOB_ERROR
            raise JobRunException('Run job error:\n%s: %s' %
                                  (exc.__class__.__name__, str(exc)))
        finally:
            job.save()
        return job.status

    def job_results(self, job):
        """
        If job is done, return results
        :param job:
        :return:
        """
        if (not job.service.allow_partial()) and (job.status < waves.const.JOB_COMPLETED):
            raise JobInconsistentStateError(job.get_status_display(),
                                            waves.const.STR_JOB_COMPLETED)
        try:
            if not job.results_available:
                # actually retrieve outputs
                self._job_results(job)
                logger.info('Job %s results', job.slug)
                job.status = waves.const.JOB_TERMINATED
            else:
                # TODO do something with results ?
                pass
        except JobException as e:
            job.status = waves.const.JOB_UNDEFINED
        finally:
            job.save()
        return job.job_outputs.all()

    def job_run_details(self, job):
        if job.status < waves.const.JOB_COMPLETED:
            raise JobInconsistentStateError(job.get_status_display(),
                                            waves.const.STATUS_LIST[1:4])
        details = None
        try:
            details = self._job_run_details(job)
        except Exception as exc:
            job.message('Error retrieving job details:\n%s:%s' %
                        (exc.__class__.__name__, str(exc)))
            job.status = waves.const.JOB_TERMINATED
        finally:
            job.save()
        return details

    def map_type(self, type_to_map):
        return self.__map_type(type_to_map)

    def dump_config(self):
        str_dump = 'Dump config for %s \n ' % self.__class__
        str_dump += 'Init params:'
        for param in self.init_params:
            str_dump += ' - %s : %s ' % (param, getattr(self, param))
        extra_dump = self._dump_config()
        return str_dump + extra_dump

    def _connect(self):
        raise NotImplementedError()

    def _disconnect(self):
        raise NotImplementedError()

    def _prepare_job(self, job):
        raise NotImplementedError()

    def _run_job(self, job):
        raise NotImplementedError()

    def _cancel_job(self, job):
        raise NotImplementedError()

    def _job_status(self, job):
        raise NotImplementedError()

    def _job_results(self, job):
        raise NotImplementedError()

    def _job_run_details(self, job):
        raise NotImplementedError()

    def _dump_config(self):
        """
        Dump current JobRunner implementation configuration
        Returns:
            <str>
        """
        return ""

    def __map_status(self, status):
        return self._states_map[status]

    def __map_type(self, type_value):
        return self._type_map[type_value]

    def _ready(self):
        return self._initialized
