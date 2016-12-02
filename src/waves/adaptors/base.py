""" Base class for all JobRunnerAdaptor implementation, define main job workflow expected behaviour """
from __future__ import unicode_literals

from django.utils.module_loading import import_string
import waves.const
from .exceptions import *
import logging
logger = logging.getLogger(__name__)


class JobRunnerAdaptor(object):
    """
    Abstract JobRunnerAdaptor class, declare expected behaviour from any WAVES's JobRunnerAdaptor

    """
    name = 'Abstract Adaptor name'
    #: Remote command for Job execution
    command = None
    #: Defined remote connector, depending on subclass implementation
    _connector = None
    #: Some connector need to parse requested job in order to create a remote job
    _parser = None
    #: Remote status need to be mapped with WAVES expected job status
    _states_map = {}
    #: List of WAVES status where job can be remotely cancelled (may be overridden in sub-classes)
    state_allow_cancel = waves.const.STATUS_LIST[0:6]
    #: Some Adaptor provide possibility to import services directly, this field declare full class name (module.class)
    importer_clazz = None

    def __init__(self, init_params={}, **kwargs):
        """ Initialize a adaptor
        Set _initialized value (True or False) if all non default expected params are set
        :raise: :class:`waves.exceptions.adaptors.AdaptorInitError` if wrong parameter given as init values
        :param init_params: a dictionnary with expected initialization params (retrieved from init_params property)
        :param kwargs: its possible to force _connector and _parser attributes when initialize a Adaptor
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
            raise AdaptorInitError(e.message)
        if all(init_param is not None for init_param in self.init_params):
            self._initialized = True
        else:
            raise AdaptorInitError('Missing parameter for adaptor init')

    @property
    def name(self):
        """ Return Adaptor displayed name """
        return self.name

    @property
    def init_params(self):
        """ Returns expected 'init_params', with default if set at class level
        :return: A dictionary containing expected init params
        :rtype: dict
        """
        return dict()

    @property
    def connected(self):
        """ Tells whether current remote adaptor object is connected to calculation infrastructure
        :return: True if actually connected / False either
        :rtype: bool
        """
        return self._connector is not None and self._connected is True

    @property
    def importer(self):
        """
        Return an Service AdaptorImporter instance, using either
        :return: an Importer new instance
        """
        if self.importer_clazz:
            importer = import_string(self.importer_clazz)
            return importer(self)
        else:
            return None

    def connect(self):
        """
        Connect to remote platform adaptor
        :raise: :class:`waves.exceptions.adaptors.AdaptorConnectException`
        :return: _connector reference or raise an
        """
        self.__ready()
        if not self.connected:
            # Do reconnect if needed
            self._connect()
        return self._connector

    def disconnect(self):
        """ Shut down connection to adaptor. Called after job adaptor execution to disconnect from remote
        :raise: :class:`waves.exceptions.adaptors.AdaptorConnectException`
        :return: Nothing
        """
        if self.connected:
            self._disconnect()
        self._connector = None
        self._connected = False

    def prepare_job(self, job):
        """ Job execution preparation process, may store prepared data in a pickled object
        :param job: The job to prepare execution for
        :raise: :class:`waves.exceptions.RunnerNotReady` if adaptor is not initialized before call
        :raise: :class:`waves.exceptions.JobPrepareException` if error during preparation process
        :raise: :class:`waves.exceptions.JobInconsistentStateError` if job status is not 'created'
        """
        self.connect()
        self._prepare_job(job)
        self.disconnect()

    def run_job(self, job):
        """ Launch a previously 'prepared' job on the remote adaptor class
        :param job: The job to launch execution
        :raise: :class:`waves.exceptions.RunnerNotReady` if adaptor is not initialized
        :raise: :class:`waves.exceptions.JobRunException` if error during launch
        :raise: :class:`waves.exceptions.JobInconsistentStateError` if job status is not 'prepared'
        """
        self.connect()
        self._run_job(job)
        self.disconnect()

    def cancel_job(self, job):
        """ Cancel a running job on adaptor class, if possible
        :param job: The job to cancel
        :return: The new job status
        :rtype: int
        :raise: :class:`waves.exceptions.JobRunException` if error during launch
        :raise: :class:`waves.exceptions.JobInconsistentStateError` if job status is not 'prepared'
        """
        self.connect()
        self._cancel_job(job)
        self.disconnect()

    def job_status(self, job):
        """ Return current WAVES Job status
        :param job: current job
        :return: one of `waves.const.STATUS_LIST`
        """
        # try:
        self.connect()
        current_state = self.__map_status(self._job_status(job))
        self.disconnect()
        return current_state

    def job_results(self, job):
        """ If job is done, return results
        :param job: current Job
        :return: a list a JobOutput
        """
        self.connect()
        self._job_results(job)
        self.disconnect()

    def job_run_details(self, job):
        """ Retrive job run details for job
        :param job: current Job
        :return: JobRunDetails object
        """
        self.connect()
        details = self._job_run_details(job)
        self.disconnect()
        return details

    def dump_config(self):
        """ Create string representation of current adaptor config"""
        str_dump = 'Dump config for %s \n ' % self.__class__
        str_dump += 'Init params:'
        for param in self.init_params:
            str_dump += ' - %s : %s ' % (param, getattr(self, param))
        extra_dump = self._dump_config()
        return str_dump + extra_dump

############################################
# Abstracts methods overridden in subclass #
############################################

    def _connect(self):
        """ Actually do connect to concrete remote job runner platform,
         :raise: `waves.adaptors.exception.AdaptorConnectException` if error
         :return: an instance of concrete connector implementation """
        raise NotImplementedError()

    def _disconnect(self):
        """ Actually disconnect from remote job runner platform
        :raise: `waves.adaptors.exception.AdaptorConnectException` if error """
        raise NotImplementedError()

    def _prepare_job(self, job):
        """ Actually do preparation for job if needed by concrete adaptor.
        For example:
            - prepare and upload input files to remote host
            - set up parameters according to concrete adaptor needs
        :raise: `waves.adaptors.exception.AdaptorException` if error """
        raise NotImplementedError()

    def _run_job(self, job):
        """ Actually launch job on concrete adaptor
        :raise: `waves.adaptors.exception.AdaptorException` if error """
        raise NotImplementedError()

    def _cancel_job(self, job):
        """ Try to cancel job on concrete adaptor
        :raise: `waves.adaptors.exception.AdaptorException` if error """
        raise NotImplementedError()

    def _job_status(self, job):
        """ Actually retrieve job states on concrete adaptor, return raw value to be mapped with defined in _states_map
        :raise: `waves.adaptors.exception.AdaptorException` if error """
        raise NotImplementedError()

    def _job_results(self, job):
        """ Retrieve job results from concrete adaptor, may include some file download from remote hosts
        Set attribute result_available for job if success
        :raise: `waves.adaptors.exception.AdaptorException` if error """
        raise NotImplementedError()

    def _job_run_details(self, job):
        """ Retrieve job run details if possible from concrete adaptor
        :raise: `waves.adaptors.exception.AdaptorException` if error """
        raise NotImplementedError()

    def _dump_config(self):
        """ Return string representation of concrete adaptor configuration
        :return: a String representing configuration """
        return ""

####################
# PRIVATES METHODS #
####################

    def __map_status(self, status):
        """ Map concrete adaptor status to WAVES expected status """
        return self._states_map[status]

    def __ready(self):
        """ Short cut to check if concrete adaptor is ready"""
        if not self._initialized:
            raise AdaptorNotReady()

