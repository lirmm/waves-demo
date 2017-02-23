"""
Test class for SAGA Runners
"""
from __future__ import unicode_literals

import logging
import os
import time
import unittest

from django.conf import settings
from waves.adaptors.core.saga_adaptors.cluster import SshUserPassClusterAdaptor
from waves.adaptors.core.saga_adaptors.shell.local import LocalShellAdaptor
from waves.adaptors.core.saga_adaptors.shell.ssh import SshUserPassShellAdaptor

import waves.tests.utils.shell_util as test_util
from waves.models import JobInput, JobOutput, Service, Job, BaseParam
from waves.tests.test_runner import TestJobRunner, sample_job
from waves.tests.utils import get_sample_dir

logger = logging.getLogger(__name__)


class ShellRunnerTestCase(TestJobRunner):
    def _set_command(self, command):
        service_command = self.service.adaptor_params.get(name='command')
        service_command.value = command
        service_command.save()
        logger.debug("service command %s", service_command.value)

    def setUp(self):

        try:
            getattr(self, 'adaptor')
        except AttributeError:
            self.adaptor = LocalShellAdaptor()
        super(ShellRunnerTestCase, self).setUp()

    def _prepare_hello_world(self):
        self._set_command(os.path.join(test_util.get_sample_dir(), 'services/hello_world.sh'))
        self.current_job = sample_job(self.service)
        self.current_job.adaptor.command = os.path.join(test_util.get_sample_dir(), 'services/hello_world.sh')
        self.current_job.job_inputs.add(
            JobInput.objects.create(job=self.current_job, value='Test Input 1', type=BaseParam.TYPE_TEXT,
                                    srv_input=None))
        self.current_job.job_inputs.add(
            JobInput.objects.create(job=self.current_job, value='Test Input 2', type=BaseParam.TYPE_TEXT,
                                    srv_input=None))
        self.current_job.outputs.add(JobOutput.objects.create(job=self.current_job, value='hello_world_output.txt',
                                                                  srv_output=None))

    def testHelloWorld(self):
        if not self.__class__.__name__ == 'ShellRunnerTestCase':
            self.skipTest("Only run with Local saga adaptor")
        self._prepare_hello_world()
        self.runJobWorkflow()
        self.assertEqual(self.current_job.status, Job.JOB_TERMINATED)
        # retrieve job run details

    @test_util.skip_unless_tool('physic_ist')
    def testPhysicIST(self, command_path='physic_ist'):
        jobs_params = self._loadServiceJobsParams(api_name='physic_ist')
        self.service.runner = self.runner_model
        self.service.adaptor = self.adaptor
        self._set_command(command_path)
        # service_submission = self.service.default_submission
        for submitted_input in jobs_params:
            self.current_job = Job.objects.create_from_submission(submission=self.service.default_submission,
                                                                  submitted_inputs=submitted_input)
            self.assertTrue(self.runJobWorkflow())

    @test_util.skip_unless_tool('services/hello_world.sh')
    def testCancelJob(self):
        if not self.__class__.__name__ == 'ShellRunnerTestCase':
            self.skipTest("Only run with Local saga adaptor")
        self._prepare_hello_world()
        self.jobs.append(self.current_job)
        self.current_job.run_prepare()
        self.assertEqual(self.current_job.status, Job.JOB_PREPARED)
        self.current_job.run_launch()
        self.assertEqual(self.current_job.status, Job.JOB_QUEUED)
        for ix in range(30):
            job_state = self.adaptor.job_status(self.current_job)
            if job_state >= Job.JOB_QUEUED:
                self.current_job.run_cancel()
                break
            else:
                time.sleep(1)
        self.assertEqual(self.current_job.status, Job.JOB_CANCELLED)

    @test_util.skip_unless_tool('cp')
    def testSimpleCP(self):
        from shutil import copyfile
        # self.adaptor.command = 'cp'
        self.service = Service.objects.get(api_name='simple-cp-10')
        self.service.adaptor = self.adaptor
        self._set_command('cp')
        self.current_job = Job.objects.create(title='Copy Job', service=self.service)
        source_file = os.path.join(get_sample_dir(), 'sample_tree.nhx')
        copyfile(source_file, os.path.join(self.current_job.working_dir, 'sample_tree.nhx'))

        self.current_job.job_inputs.add(
            JobInput.objects.create(job=self.current_job,
                                    srv_input=self.service.service_submission_inputs().get(name='input'),
                                    value='sample_tree.nhx'))
        self.current_job.job_inputs.add(
            JobInput.objects.create(job=self.current_job,
                                    srv_input=self.service.service_submission_inputs().get(name='output_name'),
                                    value=self.service.service_submission_inputs().get(name='output_name').default))
        self.current_job.outputs.add(JobOutput.objects.create(job=self.current_job,
                                                                  srv_output=self.service.service_outputs.get(
                                                                      name='Copied file')))
        self.runJobWorkflow()


class SshRunnerTestCase(ShellRunnerTestCase):
    def setUp(self):
        try:
            self.adaptor = SshUserPassShellAdaptor(init_params=dict(protocol='sge',
                                                                    user_id=settings.WAVES_TEST_SSH_USER_ID,
                                                                    crypt_user_pass=settings.WAVES_TEST_SSH_USER_PASS,
                                                                    basedir="/data/http/www/exec/waves/",
                                                                    host=settings.WAVES_TEST_SSH_HOST))
        except KeyError:
            self.skipTest("Missing one or more SSH_TEST_* environment variable")
        super(SshRunnerTestCase, self).setUp()

    def testConnect(self):
        # Only run for sub classes
        self.adaptor.connect()
        self.assertTrue(self.adaptor.connected)
        self.assertIsNotNone(self.adaptor._connector)

    def testSimpleCP(self):
        self.adaptor.connect()
        self.adaptor.command = 'cp'
        super(SshRunnerTestCase, self).testSimpleCP()

    @unittest.skip
    def testHelloWorld(self):
        pass


class SGESshUserPassRunnerTestCase(ShellRunnerTestCase):
    def setUp(self):
        self.adaptor = SshUserPassClusterAdaptor(init_params=dict(protocol='sge',
                                                                  queue=settings.WAVES_TEST_SGE_CELL,
                                                                  user_id=settings.WAVES_TEST_SSH_USER_ID,
                                                                  crypt_user_pass=settings.WAVES_TEST_SSH_USER_PASS,
                                                                  basedir="/data/http/www/exec/waves/",
                                                                  host=settings.WAVES_TEST_SSH_HOST))
        super(SGESshUserPassRunnerTestCase, self).setUp()

    def testSimpleCP(self):
        super(SGESshUserPassRunnerTestCase, self).testSimpleCP()

    def testPhysicIST(self, command_path='physic_ist'):
        super(SGESshUserPassRunnerTestCase, self).testPhysicIST('/data/http/www/binaries/physic_ist/physic_ist')

    def testConnect(self):
        super(SGESshUserPassRunnerTestCase, self).testConnect()
