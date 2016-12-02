""" Remote Galaxy API adaptor """
from __future__ import unicode_literals

from os.path import join

import bioblend
import requests
from bioblend.galaxy.client import ConnectionError
from bioblend.galaxy.objects import *
from bioblend.galaxy.objects.client import ObjToolClient
from django.utils.text import slugify
import logging
import waves.const
from waves.adaptors.api.galaxy.exception import GalaxyAdaptorConnectionError
from waves.adaptors.api.base import RemoteApiAdaptor
from waves.adaptors.exceptions import AdaptorJobException, AdaptorExecException, AdaptorConnectException
logger = logging.getLogger(__name__)

__group__ = 'Galaxy'


class GalaxyJobAdaptor(RemoteApiAdaptor):
    """This is Galaxy bioblend api WAVES adaptors, maps call to Galaxy API to expected behaviour from base class
    Expected parameters to init call (dictionary):
    **Init parameters:**
        :param host: the ip address where Galaxy is set up (default: http://localhost)
        :param username: remote user name in Galaxy server
        :param app_key: remote user's app key in Galaxy
        :param library_dir: remote library dir, where to place files in order to create galaxy histories

    """
    name = 'Galaxy remote tool adaptor (api_key)'

    #: Galaxy remote server app_key
    app_key = None
    #: Optionsl library dir (for the future :-p)
    library_dir = ""
    #: Remote tool id on Galaxy
    remote_tool_id = None
    #: Import class fully qualified name
    importer_clazz = 'waves.importers.galaxy.tool.GalaxyToolImporter'

    def __init__(self, **kwargs):
        super(GalaxyJobAdaptor, self).__init__(**kwargs)
        self._states_map = dict(
            new=waves.const.JOB_QUEUED,
            queued=waves.const.JOB_QUEUED,
            running=waves.const.JOB_RUNNING,
            waiting=waves.const.JOB_RUNNING,
            error=waves.const.JOB_ERROR,
            ok=waves.const.JOB_COMPLETED
        )

    @property
    def init_params(self):
        """
        Galaxy remote platform expected initialization parameters, defaults can be set in waves.env
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
                    remote_tool_id=self.remote_tool_id)

    def _connect(self):
        """ Create a bioblend galaxy object
        :raise: `waves.adaptors.galaxy.GalaxyAdaptorConnectionError`
        """
        try:
            self._connector = GalaxyInstance(url=self.complete_url, api_key=self.app_key)
            self._connector.gi.histories.get_current_history()
            self._connected = True
        except ConnectionError as exc:
            self._connected = False
            raise GalaxyAdaptorConnectionError(exc)

    def _disconnect(self):
        """ Setup Galaxy instance to 'disconnected' """
        self._connector = None
        self._connected = False

    def _prepare_job(self, job):
        """ - Create a new history from job data (hashkey as identifier)
            - upload job input files to galaxy in this newly created history
            - associate uploaded files galaxy id with input
        """
        import os
        try:
            history = self._connector.histories.create(name=str(job.slug))
            job.remote_history_id = history.id
            logger.debug(u'New galaxy history to ' + history.id)
            if job.input_files.count() == 0:
                logger.info("No inputs files for galaxy service ??? %s ", job)
            for job_input_file in job.input_files.all():
                file_full_path = os.path.join(job.working_dir, job_input_file.value)
                upload = history.upload_file(file_full_path, file_name=job_input_file.name)
                job_input_file.remote_input_id = upload.id
                logger.debug('Remote data id ' + job_input_file.remote_input_id + ' for ' + job_input_file.name +
                             '(' + job_input_file.value + ')')
            job.message = 'Job prepared with %i args ' % job.job_inputs.count()
            logger.debug(u'History initialized [galaxy_history_id: %s]', job.slug)
            return history.id
        except bioblend.galaxy.client.ConnectionError as e:
            exc = GalaxyAdaptorConnectionError(e)
            job.message = exc.message
            raise exc
        except IOError as e:
            raise AdaptorJobException(e, 'File upload error')

    def _run_job(self, job):
        """
        Launch the job with current parameters from associated history
        Args:
            job:
        """
        try:
            histories = self._connector.histories.get(id_=str(job.remote_history_id))
            if len(histories) == 0:
                raise AdaptorJobException(None, 'No remote history for this job, not correctly prepared ?')
            history = histories[0]
            galaxy_tool = self._connector.tools.get(id_=self.remote_tool_id)
            logger.debug('Galaxy tool connector %s', galaxy_tool)
            if galaxy_tool:
                logger.debug('Galaxy tool %s', galaxy_tool)

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
                logger.debug(u'Inputs added ' + str(inputs))
                output_data_sets = galaxy_tool.run(inputs, history=history, wait=False)
                for data_set in output_data_sets:
                    job.remote_job_id = data_set.wrapped['creating_job']
                    logger.debug(u'Job ID ' + job.remote_job_id)
                    break
                remote_job = self._connector.jobs.get(job.remote_job_id, full_details=True)
                logger.debug('Job info %s', remote_job)
                remote_outputs = remote_job.wrapped['outputs']
                for remote_output in remote_outputs:
                    output_data = remote_outputs[remote_output]
                    logger.debug('Current output %s', remote_output)
                    logger.debug('Remote output details %s', output_data)
                    logger.debug('Remote output id %s', output_data['id'])
                    job.update_output_remote_id(remote_output, output_data['id'])
                for data_set in output_data_sets:
                    logger.debug('Dataset Info %s', data_set)
                    job.update_output_value(remote_id=data_set.id,
                                            new_value='.'.join([slugify(data_set.name), data_set.file_ext]))
                    logger.debug(u'Output value updated [%s - %s]' % (
                        data_set.id, '.'.join([slugify(data_set.name), data_set.file_ext])))
                job.message = "Job queued"
            else:
                raise AdaptorExecException(None, 'Unable to retrieve associated tool %s' % self.remote_tool_id)
                # raise Exception('Test Exception')
        except requests.exceptions.RequestException as e:
            # TODO Manage specific Exception to be more precise
            job.message = 'Error in request for run %s ' % e.message
            raise AdaptorConnectException(e, 'RequestError')
        except bioblend.galaxy.client.ConnectionError as e:
            job.message = 'Connexion error for run %s:%s', (e.message, e.body)
            raise GalaxyAdaptorConnectionError(e)

    def _cancel_job(self, job):
        """ Jobs cannot be cancelled for Galaxy runners
        """
        pass

    def _job_status(self, job):
        try:
            remote_job = self._connector.jobs.get(job.remote_job_id)
            return remote_job.state
        except bioblend.galaxy.client.ConnectionError as e:
            job.message = 'Connexion error for run %s:%s', (e.message, e.body)
            raise GalaxyAdaptorConnectionError(e)

    def _job_results(self, job):
        try:
            remote_job = self._connector.jobs.get(job.remote_job_id, full_details=True)
            if remote_job:
                if remote_job.state == 'ok':
                    logger.debug('Job info %s', remote_job)
                    for job_output in job.job_outputs.all():
                        logger.debug("Retrieved data from output %s", job_output)
                        if job_output.remote_output_id:
                            self._connector.gi.histories.download_dataset(job.remote_history_id,
                                                                          job_output.remote_output_id,
                                                                          job_output.file_path,
                                                                          use_default_filename=False)

                        logger.debug("Saving output to " + job_output.file_path)
                # GET stdout / stderr from Galaxy
                with open(join(job.working_dir, job.stdout), 'a') as out, open(join(job.working_dir, job.stderr),
                                                                               'a') as err:
                    try:
                        if remote_job.wrapped['stdout']:
                            out.write(remote_job.wrapped['stdout'])
                    except KeyError:
                        logger.warning('No stdout from remote job')
                        pass
                    try:
                        if remote_job.wrapped['stderr']:
                            err.write(remote_job.wrapped['stderr'])
                    except KeyError:
                        logger.warning('No stderr from remote job')
                        pass
                job.results_available = True
                job.exit_code = remote_job.wrapped['exit_code']
            return False
        except bioblend.galaxy.client.ConnectionError as e:
            job.results_available = False
            job.message = 'Connexion error for run %s:%s', (e.message, e.body)
            raise GalaxyAdaptorConnectionError(e)

    def _job_run_details(self, job):
        remote_job = self._connector.jobs.get(job.remote_job_id, full_details=True)
        finished = None
        started = None
        extra = None
        if 'job_metrics' in remote_job.wrapped:
            for job_metric in remote_job.wrapped['job_metrics']:
                if job_metric['name'] == "end_epoch":
                    finished = job_metric['raw_value']
                if job_metric['name'] == "start_epoch":
                    started = job_metric['raw_value']
                if job_metric['name'] == "galaxy_slots":
                    extra = "%s %s" % (job_metric['value'], job_metric['title'])
        created = remote_job.wrapped['create_time']
        name = job.title
        exit_code = remote_job.wrapped['exit_code']
        details = waves.const.JobRunDetails(job.id, str(job.slug), remote_job.id, name, exit_code, created, started,
                                            finished,
                                            extra)
        logger.debug('Job Exit Code %s %s', exit_code, finished)
        galaxy_allow_purge = self._connector.gi.config.get_config()['allow_user_dataset_purge']
        # logger.warn('A least one history exist for this job, %s', len(histories))
        self._connector.histories.delete(name=str(job.slug), purge=bool(galaxy_allow_purge))
        return details

    def _dump_config(self):
        dump = "\nHost URL: %s " % self.complete_url
        if self._connected:
            dump += '(Connected)'
        return dump