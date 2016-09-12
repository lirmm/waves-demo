from __future__ import unicode_literals

import time
import os
import logging
from django.utils.timezone import localtime
from django.conf import settings
import waves.const
from waves.exceptions import *
from waves.tests import WavesBaseTestCase
from waves.adaptors import JobRunnerAdaptor
from waves.models import Service, Runner, Job, RunnerParam
import waves.settings
logger = logging.getLogger(__name__)

__all__ = ['TestBaseJobRunner', 'sample_runner']


def sample_runner(runner_impl):
    """
    Return a new adaptor model instance from adaptor class object
    Args:
        runner_impl: a JobRunnerAdaptor object
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


class TestBaseJobRunner(WavesBaseTestCase):
    """
    Test all functions in Runner adapters base class

    """

    def setUp(self):
        # Create sample data
        super(TestBaseJobRunner, self).setUp()
        try:
            getattr(self, 'adaptor')
        except AttributeError:
            self.adaptor = JobRunnerAdaptor()
        self.runner_model = sample_runner(self.adaptor)
        self.service = Service.objects.create(name="Sample Service", run_on=self.runner_model)
        self.job = None
        self._result = self.defaultTestResult()

    def tearDown(self):
        super(TestBaseJobRunner, self).tearDown()
        if self.job:
            if not settings.DEBUG:
                self.job.delete_job_dirs()
                pass

    def testConnect(self):
        if self.__module__ != 'waves.tests.test_runner':
            # Only run for sub classes
            self.adaptor.connect()
            self.assertTrue(self.adaptor.connected)
            self.assertIsNotNone(self.adaptor._connector)

    def testJobStates(self):
        """
        Test exceptions raise when inconsistency is detected in jobs
        Returns:

        """
        self.job = sample_job(self.service)
        self.job.status = waves.const.JOB_RUNNING
        length1 = self.job.job_history.count()
        logger.debug('Internal state %s, current %s', self.job._status, self.job.status)
        logger.debug('Test Prepare')
        with self.assertRaises(waves.exceptions.JobInconsistentStateError):
            self.adaptor.prepare_job(self.job)
        self.assertEqual(self.job.status, waves.const.JOB_RUNNING)
        logger.debug('Internal state %s, current %s', self.job._status, self.job.status)
        logger.debug('Test Run')
        with self.assertRaises(waves.exceptions.JobInconsistentStateError):
            self.adaptor.run_job(self.job)
        self.assertEqual(self.job.status, waves.const.JOB_RUNNING)
        logger.debug('Internal state %s, current %s', self.job._status, self.job.status)
        logger.debug('Test Cancel + inconsistent state')
        self.job.status = waves.const.JOB_COMPLETED
        with self.assertRaises(waves.exceptions.JobInconsistentStateError):
            self.adaptor.cancel_job(self.job)
        logger.debug('Internal state %s, current %s', self.job._status, self.job.status)
        # status hasn't changed
        self.assertEqual(self.job.status, waves.const.JOB_COMPLETED)
        logger.debug('%i => %s', len(self.job.job_history.values()), self.job.job_history.values())
        # assert that no history element has been added
        self.assertEqual(length1, self.job.job_history.count())

    def runJobWorkflow(self, job=None):
        if job is not None:
            self.job = job
        logger.info('Starting workflow process for job %s', self.job.title)
        self.assertEqual(1, self.job.job_history.count())
        self.adaptor.prepare_job(self.job)
        self.assertEqual(self.job.status, waves.const.JOB_PREPARED)
        remote_job_id = self.adaptor.run_job(self.job)
        logger.debug('Remote Job ID %s', remote_job_id)
        self.assertEqual(self.job.status, waves.const.JOB_QUEUED)
        for ix in range(100):
            job_state = self.adaptor.job_status(self.job)
            logger.info(u'Current job state (%i) : %s ', ix, self.job.get_status_display())
            if job_state >= waves.const.JOB_COMPLETED:
                logger.info('Job state ended to %s ', self.job.get_status_display())
                break
            else:
                time.sleep(3)
        self.assertIn(self.job.status, (waves.const.JOB_COMPLETED, waves.const.JOB_TERMINATED))
        # Get job run details
        self.adaptor.job_run_details(self.job)
        history = self.job.job_history.first()
        logger.debug("History timestamp %s", localtime(history.timestamp))
        logger.debug("Job status timestamp %s", self.job.status_time)
        self.assertTrue(self.job.results_available)
        for output_job in self.job.job_outputs.filter(may_be_empty=False):
            # TODO reactivate job output verification as soon as possible
            if not os.path.isfile(output_job.file_path):
                logger.warning("Job <<%s>> did not output expected %s (test_data/jobs/%s/) ",
                               self.job.title, output_job.value, self.job.slug)
            """
            self.assertTrue(os.path.isfile(output_job.file_path),
                            msg="Job <<%s>> did not output expected %s (test_data/jobs/%s/) " %
                                (self.job.title, output_job.value, self.job.slug))
            """
            logger.info("Expected output file: %s ", output_job.file_path)
        self.assertGreaterEqual(self.job.status, waves.const.JOB_COMPLETED)
        return True

    def testExtraUnexpectedParameter(self):
        with self.assertRaises(RunnerUnexpectedInitParam):
            self.adaptor = JobRunnerAdaptor(init_params=dict(unexpected_param='unexpected value'))
