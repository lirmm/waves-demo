from __future__ import unicode_literals

import logging
import time
import os
import json
import unittest
from django.utils.timezone import localtime

from django.test import override_settings
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

import waves.const
import waves.tests.utils.shell_util as test_util

from waves.exceptions import *
from waves.tests import WavesBaseTestCase
from waves.runners import JobRunner
from waves.models import Service, Runner, Job, RunnerParam, JobInput, JobOutput

logger = logging.getLogger(__name__)

__all__ = ['TestBaseJobRunner', 'sample_runner_model']


def sample_runner_model(runner_impl):
    """
    Return a new runner model instance from runner class object
    Args:
        runner_impl: a JobRunner object
    Returns:
        Runner model instance
    """
    runner_model = Runner.objects.create(name=runner_impl.__class__.__name__,
                                         description='Sample Runner %s' % runner_impl.__class__.__name__,
                                         clazz='%s.%s' % (runner_impl.__module__, runner_impl.__class__.__name__),
                                         available=True)
    for name, value in runner_impl.init_params.items():
        RunnerParam.objects.update_or_create(name=name, runner=runner_model, defaults={'value': value})
    return runner_model


def sample_job(service):
    """
    Return a new Job model instance for service
    Args:
        service: a Service model instance
    Returns:
        Job model instance
    """
    return Job.objects.create(title='Sample Job', service=service)


@override_settings(
    WAVES_GALAXY_URL='127.0.0.1',
    WAVES_GALAXY_API_KEY=settings.WAVES_API_TEST_KEY,
    WAVES_GALAXY_PORT='8080',
)
class TestBaseJobRunner(WavesBaseTestCase):
    """
    Test all functions in Runner adapters base class

    """

    def setUp(self):
        # Create sample data
        super(TestBaseJobRunner, self).setUp()
        try:
            getattr(self, 'runner')
        except AttributeError:
            self.runner = JobRunner()
        self.runner_model = sample_runner_model(self.runner)
        self.service = Service.objects.create(name="Sample Service", run_on=self.runner_model)
        self.job = sample_job(self.service)
        self._result = self.defaultTestResult()

    def tearDown(self):
        super(TestBaseJobRunner, self).tearDown()
        if self.current_result.wasSuccessful():
            self.job.delete_job_dirs()
            pass

    def testConnect(self):
        if self.__module__ != 'waves.tests.test_runner':
            # Only run for sub classes
            self.runner.connect()
            self.assertTrue(self.runner.connected)
            self.assertIsNotNone(self.runner._connector)

    @unittest.skip('')
    def testFailTestDoNotRemoveJobDir(self):
        with self.assertTrue(False):
            self.assertTrue(os.path.isdir(self.job.working_dir))

    def testJobStates(self):
        """
        Test exceptions raise when inconsistency is detected in jobs
        Returns:

        """
        self.job.status = waves.const.JOB_RUNNING
        length1 = self.job.job_history.count()
        logger.debug('Internal state %s, current %s', self.job._status, self.job.status)
        logger.debug('Test Prepare')
        with self.assertRaises(waves.exceptions.JobInconsistentStateError):
            self.runner.prepare_job(self.job)
        self.assertEqual(self.job.status, waves.const.JOB_RUNNING)
        logger.debug('Internal state %s, current %s', self.job._status, self.job.status)
        logger.debug('Test Run')
        with self.assertRaises(waves.exceptions.JobInconsistentStateError):
            self.runner.run_job(self.job)
        self.assertEqual(self.job.status, waves.const.JOB_RUNNING)
        logger.debug('Internal state %s, current %s', self.job._status, self.job.status)
        logger.debug('Test Cancel + inconsistent state')
        self.job.status = waves.const.JOB_COMPLETED
        with self.assertRaises(waves.exceptions.JobInconsistentStateError):
            self.runner.cancel_job(self.job)
        logger.debug('Internal state %s, current %s', self.job._status, self.job.status)
        # status hasn't changed
        self.assertEqual(self.job.status, waves.const.JOB_COMPLETED)
        logger.debug('%i => %s', len(self.job.job_history.values()), self.job.job_history.values())
        # assert that no history element has been added
        self.assertEqual(length1, self.job.job_history.count())

    def runJobWorkflow(self, job=None):
        if job is not None:
            self.job = job
        self.assertEqual(1, self.job.job_history.count())
        self.runner.prepare_job(self.job)
        self.assertEqual(self.job.status, waves.const.JOB_PREPARED)
        self.runner.run_job(self.job)
        self.assertEqual(self.job.status, waves.const.JOB_QUEUED)
        for ix in range(30):
            job_state = self.runner.job_status(self.job)
            logger.info(u'Current job state (%i) : %s ', ix, self.job.get_status_display())
            if job_state >= waves.const.JOB_COMPLETED:
                logger.info('Job state ended to %s ', self.job.get_status_display())
                break
            else:
                time.sleep(1)
        self.assertIn(self.job.status, (waves.const.JOB_COMPLETED, waves.const.JOB_TERMINATED))
        # Get job run details
        self.runner.job_run_details(self.job)
        history = self.job.job_history.first()
        logger.debug("History timestamp %s", localtime(history.timestamp))
        logger.debug("Job status timestamp %s", self.job.status_time)
        self.assertTrue(self.job.results_available)
        for output_job in self.job.job_outputs.filter(may_be_empty=False):
            logger.info("Testing file %s ", output_job.file_path)
            self.assertTrue(os.path.isfile(output_job.file_path))
            # last history

    def testExtraUnexpectedParameter(self):
        with self.assertRaises(RunnerUnexpectedInitParam):
            self.runner = JobRunner(init_params=dict(unexpected_param='unexpected value'))

    def _prepare_hello_world(self):
        self.runner.command = os.path.join(test_util.get_sample_dir(), 'services/hello_world.sh')
        JobInput.objects.create(job=self.job, name="TestInput1", value='Test Input 1',
                                param_type=waves.const.OPT_TYPE_POSIX, type=waves.const.TYPE_TEXT)
        JobInput.objects.create(job=self.job, name="TestInput2", value='Test Input 2',
                                param_type=waves.const.OPT_TYPE_POSIX, type=waves.const.TYPE_TEXT)

        JobOutput.objects.create(job=self.job, value='hello_world_output.txt', name="Output file", type="txt")

    def _preparePhysicISTJobs(self):
        """
        Test specific phyisic_ist job submission
        Returns:

        """
        jobs = []
        try:
            physic_ist_srv = Service.objects.get(api_name='physic_ist')
            logger.debug('Physic_IST service %s %s ', physic_ist_srv.name, physic_ist_srv.version)
            logger.debug('Sample dir %s ', physic_ist_srv.sample_dir)
            with open(os.path.join(physic_ist_srv.sample_dir, 'physic_ist_run.json'), 'r') as run_params:
                job_parameters = json.load(run_params)
            self.assertIsInstance(job_parameters, object)
            submitted_input = {}
            for job_params in job_parameters['physic_ist_run']:
                logger.debug('job_params: %s %s ', job_params.__class__, job_params)
                submitted_input['title'] = job_params['title']
                # All files inputs
                for key in job_params['inputs']:
                    with open(os.path.join(physic_ist_srv.sample_dir, job_params['inputs'][key])) as f:
                        submitted_input.update({key: f.read()})
                for key in job_params['params']:
                    submitted_input.update({key: job_params['params'][key]})
                jobs.append(Service.objects.create_new_job(service=physic_ist_srv, submitted_inputs=submitted_input))
        except ObjectDoesNotExist as e :
            print e.message
            self.skipTest("No physic_ist service available")
        return jobs
