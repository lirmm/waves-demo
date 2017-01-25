""" WAVES models Tests cases """
from __future__ import unicode_literals

import os
import logging
from waves.tests.base import WavesBaseTestCase
from django.utils.module_loading import import_string
from waves.models import Job, Service, Runner, JobAdminHistory, JobHistory
from waves.models.submissions import Submission
from waves.utils.encrypt import Encrypt
import waves.adaptors.const as jobconst
from waves.adaptors.base import BaseAdaptor
from django.test import TestCase

logger = logging.getLogger(__name__)


def create_runners():
    """ Create base models from all Current implementation parameters """
    from waves.utils.runners import get_runners_list
    runners = []
    for clazz in get_runners_list(raw=True):
        runners.append(Runner.objects.create(name=clazz.rsplit('.', 1)[-1].replace('Adaptor', 'Runner'), clazz=clazz))
    return runners


def create_service_for_runners():
    """ initialize a empty service for each defined runner """
    services = []
    for runner in create_runners():
        srv = Service.objects.create(name="Service %s " % runner.name, runner=runner)
        srv.submissions.add(Submission.objects.create(service=srv, label="default"))
        services.append(srv)
    return services


class TestRunner(TestCase):
    def test_create_runner(self):
        for runner in create_runners():
            logger.info('Current: %s - %s', runner.name, runner.clazz)
            adaptor = runner.adaptor
            self.assertIsInstance(adaptor, BaseAdaptor)
            self.assertEqual(runner.run_params.__len__(), adaptor.init_params.__len__())
            self.assertListEqual(sorted(runner.run_params.keys()), sorted(adaptor.init_params.keys()))
            obj_runner = import_string(runner.clazz)
            expected_params = obj_runner().init_params
            runner_params = runner.run_params
            logger.debug("Expected %s", expected_params)
            logger.debug("Defaults %s", runner_params)
            self.assertEquals(sorted(expected_params), sorted(runner_params))


class TestServices(WavesBaseTestCase):
    def test_create_service(self):
        for service in create_service_for_runners():
            self.assertEqual(service.submissions.count(), 1)
            runner_params = dict(
                {name: Encrypt.decrypt(value) if name.startswith('crypt_') else value for name, value in
                 service.runner.adaptor_params.filter(prevent_override=False).values_list('name', 'value')})
            service.runner.adaptor_params.filter(prevent_override=False).values_list('name', 'value')
            service_params = service.run_params
            # Assert that service params has a length corresponding to 'allowed override' value
            self.assertListEqual(sorted(service_params.keys()), sorted(runner_params.keys()))

    def test_service_run_param(self):
        services = Service.objects.all()
        for service in services:
            obj_runner = import_string(service.runner.clazz)
            expected_params = obj_runner().init_params
            runner_params = service.run_params
            logger.debug(expected_params)
            logger.debug(runner_params)
            self.assertEquals(sorted(expected_params.keys()), sorted(runner_params.keys()))

    def test_load_service(self):
        from os.path import join
        from waves.models.serializers.services import ServiceSerializer
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
        self.assertEqual(job.status, jobconst.JOB_CREATED)
        self.assertEqual(job.job_history.count(), 1)
        job.message = "Test job Message"
        job.status = jobconst.JOB_PREPARED
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
