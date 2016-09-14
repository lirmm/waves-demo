from __future__ import unicode_literals
import waves.const
from waves.exceptions import *
from waves.models import Job

import logging

logger = logging.getLogger(__name__)


class JobRunnerAdaptor(object):
    """
    Abstract JobRunnerAdaptor class, declare expected behaviour from any Waves's JobRunnerAdaptor
    """
    _connector = None
    _parser = None
    _type_map = {}
    _states_map = {}
    _state_allow_cancel = (waves.const.STATUS_LIST[1:5])
    importer_clazz = None

    def __init__(self, init_params={}, **kwargs):
        """
        Initialize a adaptor
        :return: a new JobRunnerAdaptor object

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
        self._initialized = all(init_param is not None for init_param in self.init_params)

    @property
    def init_params(self):
        return dict()

    @property
    def connected(self):
        return self._connector is not None and self._connected is True

    def connect(self):
        """Connect to adaptor
        :return: _connector reference or raise an ConnectionException
        """
        if self.connected:
            logger.debug('Already connected to %s', self._connector)
            return self._connector
        else:
            try:
                self._connect()
            except Exception as exc:
                logger.fatal(self.dump_config())
                self._connected = False
                raise RunnerConnectionError(str(exc), 'Connect')
            finally:
                # TODO add retry capability
                pass
        return self._connector

    def disconnect(self):
        """
        Shut down connection to adaptor. Called after job adaptor execution to disconnect from remote
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
                                  (exc.__class__.__name__, str(exc)), job=job)
        finally:
            job.save()
        return job.remote_job_id

    def cancel_job(self, job):
        """
        Cancel a running job on adaptor class
        :param job:
        :return:
        """
        if job.status not in dict(self._state_allow_cancel):
            raise JobInconsistentStateError(job.get_status_display(), self._state_allow_cancel, 'Cancel not allowed')
        try:
            if not self.connected:
                self.connect()
            if not self._ready():
                raise RunnerNotReady()
            self._cancel_job(job)
            job.status = waves.const.JOB_CANCELLED
            logger.info('Job %s cancelled ', job.slug)
        except Exception as exc:
            logger.error('Cancel job %s not applied to adaptor %s', job.pk, job.service.run_on)
            job.message = 'Could not cancel job'
            raise JobRunException('Cancel job error:\n%s: %s' %
                                  (exc.__class__.__name__, str(exc)), job=job)
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
                raise RunnerNotReady('%s adaptor not ready : \nInit_param:%s\nConnector:%s - initialized:%s' % (
                    self.__class__.__name__, self.init_params, self._connector, self._initialized))
            job.status = self.__map_status(self._job_status(job))
            if job.status == waves.const.JOB_COMPLETED:
                self.job_results(job)
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
                job.results_available = self._job_results(job)
            else:
                # TODO do something with results ?
                pass
        except JobException as e:
            job.status = waves.const.JOB_UNDEFINED
        finally:
            if job.results_available:
                job.status = waves.const.JOB_TERMINATED
            job.save()
        return job.job_outputs.all()

    def job_run_details(self, job):
        if job.status < waves.const.JOB_COMPLETED:
            raise JobInconsistentStateError(job.get_status_display(),
                                            waves.const.STATUS_LIST[1:4])
        details = None
        try:
            self._job_run_details(job)
        except Exception as exc:
            job.message('Error retrieving job details:\n%s:%s' %
                        (exc.__class__.__name__, str(exc)))
        finally:
            job.status = waves.const.JOB_TERMINATED
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
        Dump current JobRunnerAdaptor implementation configuration
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

    def _dump_job_description(self, job, job_description):
        import pickle
        import os
        with open(os.path.join(job.working_dir, 'job_description.p'), 'w+') as fp:
            pickle.dump(job_description, fp)

    def _load_job_description(self, job):
        import pickle
        import os
        with open(os.path.join(job.working_dir, 'job_description.p'), 'r') as fp:
            jd_dict = pickle.load(fp)
        return jd_dict

    def importer(self, for_service=None):
        from django.utils.module_loading import import_string
        if self.importer_clazz:
            print "importerclazz", self.importer_clazz
            importer = import_string(self.importer_clazz)
            if for_service:
                return importer(self, service=for_service)
            else:
                return importer(self)
        else:
            raise NotImplementedError
