from __future__ import unicode_literals

import logging
import json

import bioblend
import requests
from bioblend.galaxy.client import ConnectionError
from bioblend.galaxy.objects import galaxy_instance as galaxy

from django.conf import settings
from django.utils.text import slugify
from django.core.exceptions import ObjectDoesNotExist

import waves.const
from waves.exceptions import RunnerConnectionError, RunnerNotReady
from waves.models import JobOutput
from waves.runners.runner import JobRunner
import waves.settings
logger = logging.getLogger(__name__)


class GalaxyRunnerConnectionError(RunnerConnectionError):
    def __init__(self, e):
        error_data = json.loads(e.body)
        message = '{} [{}]'.format(e.message, error_data['err_msg'])
        super(GalaxyRunnerConnectionError, self).__init__(reason=message)


class GalaxyJobRunner(JobRunner):
    """
    Expected parameters to init call (dictionary):
    - host : the ip address where Galaxy is set up (default: http://localhost)
    - username : remote user name in Galaxy server
    - app_key : remote user's app key in Galaxy
    - library_dir: remote library dir, where to place files in order to create galaxy histories
    """

    host = getattr(waves.settings, 'WAVES_GALAXY_URL', None)
    port = getattr(waves.settings, 'WAVES_GALAXY_PORT', None)
    app_key = getattr(waves.settings, 'WAVES_GALAXY_API_KEY', None)
    library_dir = ""
    remote_tool_id = None

    def __init__(self, **kwargs):
        super(GalaxyJobRunner, self).__init__(**kwargs)
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
        return dict(host=self.host,
                    port=self.port,
                    app_key=self.app_key,
                    library_dir=self.library_dir,
                    remote_tool_id=self.remote_tool_id)

    def importer_clazz(self):
        return 'waves.runners.importer.galaxy.GalaxyToolImporter'

    def _connect(self):
        self._connector = bioblend.galaxy.objects.GalaxyInstance(url=self.complete_url,
                                                                 api_key=self.app_key)
        self._connected = True

    def _disconnect(self):
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
            if job.eav.galaxy_allow_purge is None:
                job.eav.galaxy_allow_purge = \
                    self._connector.gi.config.get_config()['allow_user_dataset_purge']
            if len(histories) > 1:
                logger.warn('Strange behaviours, multiple histories with same name : %s', len(histories))
                self._connector.histories.delete(name=str(job.slug), purge=bool(job.eav.galaxy_allow_purge))
                history = self._connector.histories.create(name=str(job.slug))
            elif len(histories) == 1:
                logger.debug("Retrieved only one history, maybe job is currently preparing in another process")
                history = histories[0]
            else:
                # Normal behaviour, create new history and set up file
                history = self._connector.histories.create(name=str(job.slug))
                logger.debug(u'New galaxy history to ' + history.id)
            for job_input_file in job.input_files.all():
                file_full_path = os.path.join(job.input_dir, job_input_file.value)
                upload = history.upload_file(file_full_path, file_name=job_input_file.name,
                                             file_type=os.path.splitext(file_full_path)[1][1:])
                job_input_file.eav.galaxy_input_dataset_id = upload.id
                job_input_file.save()
                logger.debug(u'Remote dataset id ' + job_input_file.eav.galaxy_input_dataset_id + u' for ' +
                             job_input_file.name + u'(' + job_input_file.value + u')')
            if job.input_files.count() == 0:
                logger.info("No inputs files for galaxy service ??? %s ", job)
            job.eav.galaxy_history_id = history.id
            job.message = 'Job prepared with %i args ' % job.job_inputs.count()
            logger.debug(u'History initialized [galaxy_history_id:' + job.eav.galaxy_history_id + u']')
            return history.id
        except RuntimeError as e:
            job.message = e.message
            raise
        except bioblend.galaxy.client.ConnectionError as e:
            exc = GalaxyRunnerConnectionError(e)
            job.message = exc.message
            raise exc
        except IOError as e:
            job.message = 'File upload error (%s) for "%s" (Details: %s)' % (
                job_input_file.name, job_input_file.eav.galaxy_input_dataset_id, e.message)
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
            history = self._connector.histories.get(job.eav.galaxy_history_id)
            galaxy_tool = self._connector.tools.get(id_=self.remote_tool_id)
            logger.debug('Galaxy tool connector %s', galaxy_tool)
            if galaxy_tool:
                logger.debug('Galaxy tool %s', galaxy_tool)

                inputs = {}
                for job_input in job.job_inputs.all():
                    if job_input.type == waves.const.TYPE_FILE:
                        index = job_input.eav.galaxy_input_dataset_id
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
                    try:
                        job_related_output = job.job_outputs.get(srv_output__name=remote_output)
                        job_related_output.eav.galaxy_output_dataset_id = output_data['id']
                    except ObjectDoesNotExist as e:
                        logger.warn('Output not retrieved from remote')
                    job_output = JobOutput.objects.get(job=job, srv_output__name=remote_output)
                    job_output.eav.galaxy_output_dataset_id = output_data['id']
                    job_output.save()
                for data_set in output_data_sets:
                    logger.debug('Dataset Info %s', data_set)
                    job_output = JobOutput.eav_objects.filter(eav__galaxy_output_dataset_id=data_set.id)[0]
                    logger.debug('Eav retrieved %s ' % job_output)
                    job_output.eav.job_output_file = '.'.join([slugify(data_set.name), data_set.file_ext])
                    logger.debug('output file name %s ' % job_output.eav.job_output_file)
                    job_output.value = job_output.eav.job_output_file
                    job_output.save()
                    logger.debug(u'Output added : %s - %s' % (job_output.eav.galaxy_output_dataset_id,
                                                              job_output.value))
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
            job.message = 'Request to runner error for run %s ', e.message
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
            logger.debug('Job info %s', remote_job)
            for job_output in job.job_outputs.all():
                logger.debug("Retrieved data from output %s", job_output)
                if job_output.eav.galaxy_output_dataset_id:
                    self._connector.gi.histories.download_dataset(job.eav.galaxy_history_id,
                                                                  job_output.eav.galaxy_output_dataset_id,
                                                                  job_output.file_path,
                                                                  use_default_filename=False)
                logger.debug("Saving output to " + job_output.file_path)
                job_output.save()
            return True
        return False

    def _job_run_details(self, job):
        # logger.warn('Not method run details for %s' % self.__class__)
        # remote_job = self._connector.jobs.get(job.remote_job_id, full_details=True)
        # TODO actually get run details
        pass

    @property
    def complete_url(self):
        return ':'.join([self.host, self.port])

    def _dump_config(self):
        dump = ""
        if self._connected:
            dump = 'Connect to galaxy setup %s' % self._connector.gi.config
        return dump


class GalaxyWorkFlowRunner(GalaxyJobRunner):
    def importer_clazz(self):
        return 'waves.runners.importer.galaxy.GalaxyWorkFlowImporter'

    def _run_job(self, job):
        """
        From data prepared in galaxy, launch a new workflow identified by 'remote_tool_id'
        Args:
            job: Job model instance
        Returns:
            None
        """
        raise NotImplementedError()

    def _cancel_job(self, job):
        """Workflow invocation can be cancelled is not already launched
        """
        raise NotImplementedError()

    def _job_status(self, job):
        raise NotImplementedError()

    def _job_results(self, job):
        raise NotImplementedError()
