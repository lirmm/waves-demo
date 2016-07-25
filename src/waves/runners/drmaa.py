from __future__ import unicode_literals, absolute_import

import json
import logging
import os
import pickle
import time

from django.conf import settings
from django.utils import timezone, formats
from django.core.exceptions import ObjectDoesNotExist

import waves.const
from waves.exceptions import RunnerNotInitialized
from waves.runners.lib.lib_drmaa import DrmaaSessionFactory
from waves.runners.runner import JobRunner
from waves.models import ServiceExitCode

logger = logging.getLogger(__name__)
drmaa = None


class DRMAAJobRunner(JobRunner):
    """
    DRMAA Compliant base job runner class
    Author: Marc Chakiachvili
    Version: __version__
    """
    drmaa_lib = settings.WAVES_DRMAA_LIBRARY_PATH
    command = None
    _connector = None

    def __init__(self, **kwargs):
        global drmaa
        if 'drmaa_lib' in kwargs:
            logger.info('Overriding DRMAA_LIBRARY_PATH due to runner plugin parameter: %s',
                        kwargs['drmaa_lib'])
            self.drmaa_lib = kwargs['drmaa_lib']
            os.environ['DRMAA_LIBRARY_PATH'] = self.drmaa_lib
        super(DRMAAJobRunner, self).__init__(**kwargs)
        try:
            drmaa = __import__('drmaa')
        except (ImportError, RuntimeError) as exc:
            raise RunnerNotInitialized('The Python drmaa package is required to use this '
                                       'feature, correct the following error:\n%s: %s' %
                                       (RunnerNotInitialized, str(exc)))

        self._states_map = {
            drmaa.JobState.UNDETERMINED: waves.const.JOB_UNDEFINED,
            drmaa.JobState.QUEUED_ACTIVE: waves.const.JOB_QUEUED,
            drmaa.JobState.SYSTEM_ON_HOLD: waves.const.JOB_QUEUED,
            drmaa.JobState.USER_ON_HOLD: waves.const.JOB_QUEUED,
            drmaa.JobState.USER_SYSTEM_ON_HOLD: waves.const.JOB_QUEUED,
            drmaa.JobState.RUNNING: waves.const.JOB_RUNNING,
            drmaa.JobState.SYSTEM_SUSPENDED: waves.const.JOB_SUSPENDED,
            drmaa.JobState.USER_SUSPENDED: waves.const.JOB_SUSPENDED,
            drmaa.JobState.DONE: waves.const.JOB_COMPLETED,
            drmaa.JobState.FAILED: waves.const.JOB_ERROR,
        }

    @property
    def init_params(self):
        return dict(drmaa_lib=self.drmaa_lib, command=self.command)

    @property
    def connected(self):
        return self._connector is not None and self._connected is True

    def _connect(self):
        self._connector = DrmaaSessionFactory().get()
        self._connected = True

    def _disconnect(self):
        DrmaaSessionFactory().get().close()
        self._connector.session = None

    def _prepare_job(self, job):
        try:
            jt = dict(
                remoteCommand=self.command,
                jobName=str(job.title),
                workingDirectory="%s" % job.working_dir,
                outputPath=":%s.out" % job.output_dir,
                errorPath=":%s.err" % job.output_dir,
                args=job.command.get_command_line_element_list(job.job_inputs.all())
                # args=self.__get_command_line(job)
            )
            self.__get_command_line(job)
            filename = "%s/job_template.json" % job.working_dir
            with open(filename, 'w+') as fp:
                json.dump(jt, fp)
            job.message = 'Job prepared at ' + formats.date_format(timezone.localtime(timezone.now()),
                                                                   "SHORT_DATETIME_FORMAT")
        except IOError as e:
            job.message = e.message
            raise
        except RuntimeError as e:
            job.message = e.message
            raise

    def _run_job(self, job):
        with open("%s/job_template.json" % job.working_dir, 'r') as fp:
            jt_data = json.load(fp)
        try_num = 0
        while job.remote_job_id is None and try_num < 5:
            try:
                job.remote_job_id = self._connector.run_job(**jt_data)
                job.status = waves.const.JOB_QUEUED
                logger.debug('Job submitted with ID %s' % job.remote_job_id)
                job.message = 'Job submitted to runner (remote id %s)' % job.remote_job_id
                break
            except (drmaa.InternalException, drmaa.DeniedByDrmException) as e:
                try_num += 1
                logger.warning('(%s) drmaa.Session.runJob() failed, will retry: %s', job.slug, e)
                fail_msg = "Unable to run this job due to a cluster error, please retry it later"
                job.message = fail_msg
                time.sleep(5)
                job.message = "(%s) All attempts to submit job failed" % job.slug
                job.status = waves.const.JOB_ERROR
            except Exception as e:
                logger.exception('(%s) drmaa.Session.runJob() failed unconditionally (%s)', job.slug, e)
                try_num = 5
                job.message = "(%s) All attempts to submit job failed" % job.slug
                job.status = waves.const.JOB_ERROR

    def _cancel_job(self, job):
        self._connector.kill(job.remote_job_id)

    def _job_status(self, job):
        try:
            remote_state = self._connector.job_status(job.remote_job_id)
            return remote_state
        except (drmaa.InternalException, drmaa.InvalidJobException) as e:
            e.message = job.remote_job_id + ' ' + e.message
            job.message = e.message
            raise
        except drmaa.DrmCommunicationException as e:
            job.message = 'Could not contact runner %s' % e.message
            job.status = waves.const.JOB_UNDEFINED
            raise

    def _job_results(self, job):
        # TODO get actual result code from DRMAA
        job.exit_code = 0
        return job.exit_code == 0

    def _job_run_details(self, job):
        # TODO setup storage for run details
        if os.path.isfile(os.path.join(job.working_dir, 'run_details.p')):
            try:
                with open(os.path.join(job.working_dir, 'run_details.p'), 'r') as fp:
                    job_info = pickle.load(fp)
                logger.debug('JobInfo %s %s', job_info, job_info.__class__.__name__)
                return job_info
            except pickle.UnpicklingError as e:
                logger.warn('Error retrieving data from pickle %s', e.message)
                pass
        details = None
        # Run details has not been retrieved
        try:
            details = self._connector.job_info(job.remote_job_id)
            job.exit_code = details.exitStatus
            # TODO check if convention related ?
            if job.exit_code != 0:
                job.status = waves.const.JOB_ERROR
                try:
                    exit_code = ServiceExitCode.objects.get(exit_code=job.exit_code)
                    job.message = exit_code.message
                except ObjectDoesNotExist:
                    pass
            # from datetime import datetime
            from django.utils.timezone import datetime, get_current_timezone
            job.status_time = datetime.fromtimestamp(float(details.resourceUsage['end_time']),
                                                     tz=get_current_timezone())

            # TODO add run details in eav values
            with open(os.path.join(job.working_dir, 'run_details.p'), 'w+') as fp:
                pickle.dump(details, fp)
            logger.info('Job details: %s %s', details, details.__class__.__name__)

        except KeyError:
            job.status_time = None
            # TODO add constant to manage 'standard exit code'
            # job.exit_code = -999
        except drmaa.ExitTimeoutException:
            logger.info('Timeout reaching job details %s', job.remote_job_id)
        except drmaa.DrmCommunicationException as e:
            logger.info('Could not contact runner %s: %s', job.remote_job_id, e.message)
        except drmaa.InvalidJobException as e:
            logger.info('Could not retrieve job info from id %s: %s', job.remote_job_id, e.message)
        except Exception as e:
            logger.info('Unexpected Exception %s: %s %s', job.remote_job_id, e.message, e.__class__.__name__)
        return details

    def _dump_config(self):
        if self._connected:
            dump_template = 'A DRMAA object was created \n' \
                            'Supported contact strings: %s\n' \
                            'Supported DRM systems: %s\n' \
                            'Supported DRMAA implementations: %s\n' \
                            'Version %s'
            return dump_template % (
                self._connector.session.contact, self._connector.session.drmsInfo,
                self._connector.session.drmaaImplementation,
                str(self._connector.session.version))
        return ""

    def _ready(self):
        return self._initialized and self.command is not None
