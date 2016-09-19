from __future__ import unicode_literals

import os
import logging

from django.test import TestCase
from django.utils.module_loading import import_string

from waves.models import Job, Service, Runner, JobAdminHistory, JobHistory
import waves.const

logger = logging.getLogger(__name__)


class TestRunners(TestCase):

    def test_runners_defaults(self):
        for runner in Runner.objects.exclude(clazz__isnull=True):
            obj_runner = import_string(runner.clazz)
            logger.debug("Clazz %s", runner.clazz)
            expected_params = obj_runner().init_params
            runner_params = runner.default_run_params()
            logger.debug("Expected %s", expected_params)
            logger.debug("Defaults %s", runner_params)
            self.assertEquals(sorted(expected_params), sorted(runner_params))


class TestServices(TestCase):

    def test_create_service(self):
        runner = Runner.objects.create(name="Sample runner", clazz="waves.adaptors.mock.MockJobAdaptor")
        srv = Service.objects.create(name="Sample Service", run_on=runner)
        self.assertIsNotNone(srv.default_submission)
        pass

    def test_service_run_param(self):
        services = Service.objects.all()
        for service in services:
            obj_runner = import_string(service.run_on.clazz)
            expected_params = obj_runner().init_params
            runner_params = service.run_params()
            logger.debug(expected_params)
            logger.debug(runner_params)
            self.assertEquals(sorted(expected_params.keys()), sorted(runner_params.keys()))


class TestJobs(TestCase):
    def setUp(self):
        super(TestJobs, self).setUp()

    def tearDown(self):
        super(TestJobs, self).tearDown()

    def test_jobs_signals(self):
        job = Job.objects.create(service=Service.objects.create(name='Sample Service'))
        self.assertIsNotNone(job.title)
        self.assertTrue(os.path.isdir(job.working_dir))
        self.assertTrue(os.path.isdir(job.input_dir))
        self.assertTrue(os.path.isdir(job.output_dir))
        logger.debug('Job directories has been created')
        self.assertEqual(job.status, waves.const.JOB_CREATED)
        job_history = job.job_history.all()
        self.assertEqual(len(job_history), 1)
        job.delete()
        self.assertFalse(os.path.isdir(job.working_dir))
        logger.debug('Job directories has been deleted')

    def test_job_history(self):
        job = Job.objects.create(service=Service.objects.create(name='Sample Service'))
        admin_hist = JobAdminHistory.objects.create(job=job, message="Test Admin message", status=job.status)
        job.job_history.add(admin_hist)
        job.job_history.add(JobHistory.objects.create(job=job, message="Test public message", status=job.status))
        self.assertEqual(job.job_history.count(), 3)
        self.assertEqual(job.public_history.count(), 2)
