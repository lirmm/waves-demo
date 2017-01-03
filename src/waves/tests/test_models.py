from __future__ import unicode_literals

import os
import logging

from waves.tests.base import WavesBaseTestCase
from django.utils.module_loading import import_string

from waves.models import Job, Service, Runner, JobAdminHistory, JobHistory
from waves.models.submissions import Submission
from waves.models.serializers.services import ServiceSerializer
import waves.const

logger = logging.getLogger(__name__)


class TestRunners(WavesBaseTestCase):
    def test_runners_defaults(self):
        for runner in Runner.objects.all():
            obj_runner = import_string(runner.clazz)
            logger.debug("Clazz %s", runner.clazz)
            expected_params = obj_runner().init_params
            runner_params = runner.default_run_params()
            logger.debug("Expected %s", expected_params)
            logger.debug("Defaults %s", runner_params)
            self.assertEquals(sorted(expected_params), sorted(runner_params))


class TestServices(WavesBaseTestCase):
    def test_create_service(self):
        runner = Runner.objects.create(name="SubmissionSample runner", clazz='waves.tests.mocks.adaptor.MockJobRunnerAdaptor')
        srv = Service.objects.create(name="SubmissionSample Service", runner=runner)
        srv.submissions.add(Submission.objects.create(service=srv, label="SubmissionSample submission"))
        self.assertEqual(srv.submissions.count(), 1)

    def test_service_run_param(self):
        services = Service.objects.all()
        for service in services:
            obj_runner = import_string(service.runner.clazz)
            expected_params = obj_runner().init_params
            runner_params = service.run_params()
            logger.debug(expected_params)
            logger.debug(runner_params)
            self.assertEquals(sorted(expected_params.keys()), sorted(runner_params.keys()))

    def test_load_service(self):
        from os.path import join
        import json
        from django.conf import settings
        init_count = Service.objects.all().count()
        file_paths = []
        for srv in Service.objects.all():
            file_paths.append(srv.serialize())
        for exp in file_paths:
            with open(exp) as fp:
                serializer = ServiceSerializer(data=json.load(fp))
                if serializer.is_valid():
                    serializer.save()
        self.assertEqual(init_count * 2, Service.objects.all().count())


class TestJobs(WavesBaseTestCase):
    def setUp(self):
        super(TestJobs, self).setUp()

    def tearDown(self):
        super(TestJobs, self).tearDown()

    def test_jobs_signals(self):
        job = Job.objects.create(service=Service.objects.create(name='SubmissionSample Service'))
        self.assertIsNotNone(job.title)
        self.assertTrue(os.path.isdir(job.working_dir))
        logger.debug('Job directories has been created %s ', job.working_dir)
        self.assertEqual(job.status, waves.const.JOB_CREATED)
        self.assertEqual(job.job_history.count(), 1)
        job.message = "Test job Message"
        job.status = waves.const.JOB_PREPARED
        job.save()
        self.assertEqual(job.job_history.count(), 2)
        self.assertEqual(job.job_history.first().message, job.message)
        job.delete()
        self.assertFalse(os.path.isdir(job.working_dir))
        logger.debug('Job directories has been deleted')

    def test_job_history(self):
        job = Job.objects.create(service=Service.objects.create(name='SubmissionSample Service'))
        job.job_history.add(JobAdminHistory.objects.create(job=job, message="Test Admin message", status=job.status))
        job.job_history.add(JobHistory.objects.create(job=job, message="Test public message", status=job.status))
        try:
            self.assertEqual(job.job_history.count(), 3)
            self.assertEqual(job.public_history.count(), 2)
        except AssertionError:
            logger.debug('All history %s', job.job_history.all())
            logger.debug('Public history %s', job.public_history.all())
            raise
