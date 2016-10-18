"""
Galaxy bioblend API job runne adaptor
"""
from __future__ import unicode_literals

import json

import bioblend
import requests
from bioblend.galaxy.client import ConnectionError
from bioblend.galaxy.objects import galaxy_instance as galaxy
from django.utils.text import slugify
from django.core.exceptions import ObjectDoesNotExist

import waves.const
from waves.exceptions import *
from waves.models import JobOutput
from waves.adaptors.runner import JobRunnerAdaptor
import waves.settings


class GalaxyAdaptorConnectionError(RunnerConnectionError):
    """
    Specific subclass for managing Galaxy service connection errors

    """

    def __init__(self, e):
        """
        Load and parse superclass ConnectionError message body
        :param e: The exception
        """
        error_data = json.loads(e.body)
        message = '{} [{}]'.format(e.message, error_data['err_msg'])
        super(GalaxyAdaptorConnectionError, self).__init__(reason=message)


class GalaxyJobAdaptor(JobRunnerAdaptor):
    """This is Galaxy bioblend api WAVES adaptors, maps call to Galaxy API to expected behaviour from base class

    Expected parameters to init call (dictionary):

    **Init parameters:**
        :param host: the ip address where Galaxy is set up (default: http://localhost)
        :param username: remote user name in Galaxy server
        :param app_key: remote user's app key in Galaxy
        :param library_dir: remote library dir, where to place files in order to create galaxy histories

    """

    host = '127.0.0.1'
    port = '8080'
    app_key = None
    library_dir = ""
    remote_tool_id = None
    importer_clazz = 'waves.adaptors.importer.galaxy.GalaxyToolImporter'

    def __init__(self, **kwargs):
        super(GalaxyJobAdaptor, self).__init__(**kwargs)
        self._states_map = dict(
            new=waves.const.JOB_RUNNING,
            queued=waves.const.JOB_QUEUED,
            running=waves.const.JOB_RUNNING,
            waiting=waves.const.JOB_QUEUED,
            error=waves.const.JOB_ERROR,
            ok=waves.const.JOB_COMPLETED
        )
        self._type_map = dict(
            text=waves.const.TYPE_TEXT,
            boolean=waves.const.TYPE_BOOLEAN,
            integer=waves.const.TYPE_INTEGER,
            float=waves.const.TYPE_FLOAT,
            data=waves.const.TYPE_FILE,
            select=waves.const.TYPE_LIST,
            conditional=waves.const.TYPE_LIST,
            data_column=waves.const.TYPE_TEXT,
            data_collection=waves.const.TYPE_FILE,
        )

    @property
    def init_params(self):
        """
        List Galaxy adaptor expected initialization parameters, defaults can be set in waves.env

        - **returns**
            - host: Galaxy full host url
            - port: Galaxy host port
            - app_key: Galaxy remote user api_key
            - library_dir: Galaxy remote user library, no default
            - remote_tool_id: Galaxy remote tool id, should be set for each Service, no default

        :return: A dictionary containing expected init params
        :rtype: dict
        """
        return dict(host=self.host,
                    port=self.port,
                    app_key=self.app_key,
                    library_dir=self.library_dir,
                    remote_tool_id=self.remote_tool_id)

    def _connect(self):
        """
        Actually connect to remote Galaxy Instance

        :raise: `waves.adaptors.galaxy.GalaxyAdaptorConnectionError`
        :return: Nothing
        :rtype:None
        """
        try:
            self._connector = bioblend.galaxy.objects.GalaxyInstance(url=self.complete_url,
                                                                     api_key=self.app_key)
            self._connected = True
        except ConnectionError as exc:
            raise GalaxyAdaptorConnectionError(exc)

    def _disconnect(self):
        """
        Setup instance to disconnected

        :return: Nothing
        :rtype: None
        """
        self._connector = None
        self._connected = False

    def _prepare_job(self, job):
        """
        - Create a new history from job data (hashkey as identifier)
        - upload job input files to galaxy in this newly created history
            - associate uploaded files galaxy id with input
        Raises:
            RunnerNotInitialized
        Args:
            job: the job to prepare

        Returns:
            None
        """
        import os
        try:
            histories = self._connector.histories.list(name=str(job.slug))
            galaxy_allow_purge = self._connector.gi.config.get_config()['allow_user_dataset_purge']
            if len(histories) >= 1:
                self.logger.warn('A least one history exist for this job, %s', len(histories))
                self._connector.histories.delete(name=str(job.slug), purge=bool(galaxy_allow_purge))
                history = self._connector.histories.create(name=str(job.slug))
            else:
                # Normal behaviour, create new history and set up file
                history = self._connector.histories.create(name=str(job.slug))
                self.logger.debug(u'New galaxy history to ' + history.id)
            for job_input_file in job.input_files.all():
                file_full_path = os.path.join(job.input_dir, job_input_file.value)
                """
                was :
                upload = history.upload_file(file_full_path, file_name=job_input_file.name,
                                             file_type=os.path.splitext(file_full_path)[1][1:])
                """
                upload = history.upload_file(file_full_path, file_name=job_input_file.name)
                job_input_file.remote_input_id = upload.id
                job_input_file.save()
                self.logger.debug(u'Remote dataset id ' + job_input_file.remote_input_id + u' for ' +
                                    job_input_file.name + u'(' + job_input_file.value + u')')
            if job.input_files.count() == 0:
                self.logger.info("No inputs files for galaxy service ??? %s ", job)
            job.remote_history_id = history.id
            job.message = 'Job prepared with %i args ' % job.job_inputs.count()
            self.logger.debug(u'History initialized [galaxy_history_id: %s]', job.slug)
            return history.id
        except RuntimeError as e:
            job.message = e.message
            raise
        except bioblend.galaxy.client.ConnectionError as e:
            exc = GalaxyAdaptorConnectionError(e)
            job.message = exc.message
            raise exc
        except IOError as e:
            job.message = 'File upload error (%s) for "%s" (Details: %s)' % (
                job_input_file.name, job_input_file.remote_input_id, e.message)
            raise
        except Exception as e:
            job.message = 'Job preparation error (%s) "%s" ' % (e.__class__.__name__, e.message)
            raise

    def _run_job(self, job):
        """
        Launch the job with current parameters from associated history
        Args:
            job:
        """
        try:
            histories = self._connector.histories.list(name=str(job.slug), deleted=False)
            if len(histories) > 1:
                raise JobRunException('Inconsistent remote state - multiple histories for this job')
            else:
                history = histories[0]
            galaxy_tool = self._connector.tools.get(id_=self.remote_tool_id)
            self.logger.debug('Galaxy tool connector %s', galaxy_tool)
            if galaxy_tool:
                self.logger.debug('Galaxy tool %s', galaxy_tool)

                inputs = {}
                for job_input in job.job_inputs.all():
                    if job_input.type == waves.const.TYPE_FILE:
                        index = job_input.remote_input_id
                        value = job_input.name
                    else:
                        index = job_input.name
                        value = job_input.value
                    if value != 'None':
                        inputs[index] = value
                self.logger.debug(u'Inputs added ' + str(inputs))
                output_data_sets = galaxy_tool.run(inputs, history=history, wait=False)
                for data_set in output_data_sets:
                    job.remote_job_id = data_set.wrapped['creating_job']
                    self.logger.debug(u'Job ID ' + job.remote_job_id)
                    break
                remote_job = self._connector.jobs.get(job.remote_job_id, full_details=True)
                self.logger.debug('Job info %s', remote_job)
                remote_outputs = remote_job.wrapped['outputs']
                # print "remote outputs ", remote_outputs
                for remote_output in remote_outputs:
                    output_data = remote_outputs[remote_output]
                    self.logger.debug('Current output %s', remote_output)
                    self.logger.debug('Remote output details %s', output_data)
                    self.logger.debug('Remote output id %s', output_data['id'])
                    try:
                        job_related_output = job.job_outputs.get(srv_output__name=remote_output)
                        job_related_output.remote_output_id = output_data['id']
                        job_output = JobOutput.objects.get(job=job, srv_output__name=remote_output)
                        job_output.remote_output_id = output_data['id']
                        job_output.save()
                    except ObjectDoesNotExist as e:
                        self.logger.warn('Output not retrieved/expected from remote %s', remote_output)
                for data_set in output_data_sets:
                    self.logger.debug('Dataset Info %s', data_set)
                    try:
                        job_output = JobOutput.objects.get(remote_output_id=data_set.id)
                        job_output.value = '.'.join([slugify(data_set.name), data_set.file_ext])
                        job_output.save()
                    except ObjectDoesNotExist as e:
                        self.logger.warn('OutputDataset not retrieved/expected from remote %s', data_set.id)
                    self.logger.debug(u'Output added[%s - %s]' % (job_output.remote_output_id, job_output.value))
                job.message = "Job queued"
                # raise Exception('Test Exception')
        except requests.exceptions.RequestException as e:
            # TODO Manage specific Exception to be more precise
            job.message = 'Error in request for run %s ' % e.message
            raise
        except bioblend.galaxy.client.ConnectionError as e:
            job.message = 'Connexion error for run %s:%s', (e.message, e.body)
            raise
        except requests.exceptions.RequestException as e:
            job.message = 'Request to adaptor error for run %s ', e.message
            raise

    def _cancel_job(self, job):
        """Jobs cannot be cancelled for Galaxy runners
        """
        pass

    def _job_status(self, job):
        remote_job = self._connector.jobs.get(job.remote_job_id)
        return remote_job.state

    def _job_results(self, job):
        remote_job = self._connector.jobs.get(job.remote_job_id, full_details=True)
        if remote_job and remote_job.state == 'ok':
            self.logger.debug('Job info %s', remote_job)
            for job_output in job.job_outputs.all():
                self.logger.debug("Retrieved data from output %s", job_output)
                if job_output.remote_output_id:
                    self._connector.gi.histories.download_dataset(job.remote_history_id,
                                                                  job_output.remote_output_id,
                                                                  job_output.file_path,
                                                                  use_default_filename=False)
                self.logger.debug("Saving output to " + job_output.file_path)
                # job_output.save()
            return True
        return False

    def _job_run_details(self, job):
        # self.logger.warn('Not method run details for %s' % self.__class__)
        # remote_job = self._connector.jobs.get(job.remote_job_id, full_details=True)
        # TODO actually get run details
        pass

    @property
    def complete_url(self):
        return ':'.join([self.host, self.port])

    def _dump_config(self):
        dump = "\nHost URL: %s " % self.complete_url
        if self._connected:
            dump += '(Connected)'
        return dump


class GalaxyWorkFlowAdaptor(GalaxyJobAdaptor):
    """Dedicated Adaptor to run / import / follow up Galaxy Workflow execution

    .. WARNING::
        This class is not fully implemented at the moment !

    As it inherit from :class:`waves.adaptors.GalaxyJobAdaptor`, its init paramas are the same.

    """
    #: Dedicated import clazz for Galaxy workflows see :class:`waves.adaptors.importer.galaxy.GalaxyWorkFlowImporter`
    importer_clazz = 'waves.adaptors.importer.galaxy.GalaxyWorkFlowImporter'

    def _run_job(self, job):
        """
        :param job: Job to run
        :raise: NotImplementedError
        """
        raise NotImplementedError()

    def _cancel_job(self, job):
        """
        :param job: Job to cancel
        :raise: NotImplementedError
        """
        raise NotImplementedError()

    def _job_status(self, job):
        """
        :param job: Job to show status
        :raise: NotImplementedError
        """
        raise NotImplementedError()

    def _job_results(self, job):
        """
        :param job: Job to retrieve result for
        :raise: NotImplementedError
        """
        raise NotImplementedError()
