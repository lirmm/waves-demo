"""
Test class for SAGA Runners
"""
from __future__ import unicode_literals

import os
import time
from unittest import skip
import waves.const
import waves.tests.utils.shell_util as test_util
from waves.tests.test_runner import TestBaseJobRunner, sample_job
from waves.adaptors.sge import SGEJobAdaptor, SGEOverSSHAdaptor
from waves.adaptors.local import ShellJobAdaptor
from waves.adaptors.ssh import SshUserPassJobAdaptor
from waves.models import JobInput, JobOutput
from waves.adaptors.sge import SGEOverSSHAdaptor
from waves.managers.servicejobs import ServiceJobManager
from waves.tests.utils import get_sample_dir
import waves.settings


class SAGARunnerTestCase(TestBaseJobRunner):
    def setUp(self):
        self.adaptor = ShellJobAdaptor()
        super(SAGARunnerTestCase, self).setUp()

    def _prepare_hello_world(self):
        self.adaptor.command = os.path.join(test_util.get_sample_dir(), 'services/hello_world.sh')
        self.current_job = sample_job(self.service)
        self.current_job.job_inputs.add(
            JobInput.objects.create(job=self.current_job, value='Test Input 1', srv_input=None))
        self.current_job.job_inputs.add(
            JobInput.objects.create(job=self.current_job, value='Test Input 2', srv_input=None))
        self.current_job.job_outputs.add(JobOutput.objects.create(job=self.current_job, value='hello_world_output.txt',
                                                                  srv_output=None))

    def testHelloWorld(self):
        self._prepare_hello_world()
        self.runJobWorkflow()
        self.assertEqual(self.current_job.status, waves.const.JOB_TERMINATED)

    @test_util.skip_unless_tool('physic_ist')
    def testPhysicIST(self):
        jobs_params = self._loadServiceJobsParams(api_name='physic_ist')
        self.adaptor.command = 'physic_ist'
        # service_submission = self.service.default_submission
        for submitted_input in jobs_params:
            self.current_job = ServiceJobManager.create_new_job(submission=self.service.default_submission,
                                                                submitted_inputs=submitted_input)
            self.assertTrue(self.runJobWorkflow())
            # self.fail('Failed message')

    @test_util.skip_unless_tool('services/hello_world.sh')
    def testCancelJob(self):
        self._prepare_hello_world()
        self.jobs.append(self.current_job)
        self.adaptor.prepare_job(self.current_job)
        self.assertEqual(self.current_job.status, waves.const.JOB_PREPARED)
        self.adaptor.run_job(self.current_job)
        self.assertEqual(self.current_job.status, waves.const.JOB_QUEUED)
        for ix in range(30):
            job_state = self.adaptor.job_status(self.current_job)
            if job_state > waves.const.JOB_QUEUED:
                self.adaptor.cancel_job(self.current_job)
                break
            else:
                time.sleep(1)
        self.assertEqual(self.current_job.status, waves.const.JOB_CANCELLED)

    @test_util.skip_unless_tool('cp')
    def testSimpleCP(self):
        self.adaptor.command = 'cp'
        self.current_job = sample_job(self.service)
        self.current_job.job_inputs.add(JobInput.objects.create(job=self.current_job, srv_input=None,
                                                                value=os.path.join(get_sample_dir(),
                                                                                   'sample_tree.nhx')))
        self.current_job.job_inputs.add(JobInput.objects.create(job=self.current_job, srv_input=None,
                                                                value=self.current_job.output_dir))
        self.current_job.job_outputs.add(JobOutput.objects.create(job=self.current_job, srv_output=None,
                                                                  value='sample_tree.nhx'))

        self.runJobWorkflow()

    @test_util.skip_unless_tool('fastme')
    @skip('Fastme test need refactoring\n')
    def testFastME(self):
        self.adaptor.command = 'fastme'
        JobInput.objects.create(job=self.current_job, name="input_data", type=waves.const.TYPE_FILE,
                                param_type=waves.const.OPT_TYPE_VALUATED,
                                value=os.path.join(get_sample_dir(), 'fast_me', 'nucleic.phy'))
        JobInput.objects.create(job=self.current_job, name="dna", type=waves.const.TYPE_TEXT,
                                param_type=waves.const.OPT_TYPE_VALUATED,
                                value='J')
        output_tree = JobInput.objects.create(job=self.current_job, name="output_tree", type=waves.const.TYPE_TEXT,
                                              param_type=waves.const.OPT_TYPE_VALUATED,
                                              value='output_tree.txt')
        output_matrix = JobInput.objects.create(job=self.current_job, name="output_matrix", type=waves.const.TYPE_TEXT,
                                                param_type=waves.const.OPT_TYPE_VALUATED,
                                                value='output_matrix.txt')
        output_info = JobInput.objects.create(job=self.current_job, name='output_info', type=waves.const.TYPE_TEXT,
                                              param_type=waves.const.OPT_TYPE_VALUATED,
                                              value="output_info.txt")
        # associated outputs
        JobOutput.objects.create(job=self.current_job, name='Inferred tree file',
                                 value=output_tree.value)
        JobOutput.objects.create(job=self.current_job, name="Computed matrix",
                                 value=output_matrix.value)
        JobOutput.objects.create(job=self.current_job, name="Output Info",
                                 value=output_info.value)
        self.runJobWorkflow()


class SshRunnerTestCase(SAGARunnerTestCase):
    def setUp(self):
        try:
            self.adaptor = SshUserPassJobAdaptor(init_params=dict(user_id=waves.settings.WAVES_TEST_SSH_USER_ID,
                                                                  user_pass=waves.settings.WAVES_TEST_SSH_USER_PASS,
                                                                  host=waves.settings.WAVES_TEST_SSH_HOST))
        except KeyError:
            self.skipTest("Missing one or more SSH_TEST_* environment variable")
        super(SshRunnerTestCase, self).setUp()


@test_util.skip_unless_sge()
class SgeRunnerTestCase(SAGARunnerTestCase):
    def setUp(self):
        self.adaptor = SGEJobAdaptor(init_params=dict(queue=waves.settings.WAVES_TEST_SGE_CELL))
        super(SgeRunnerTestCase, self).setUp()

    @test_util.skip_unless_tool('physic_ist')
    def testPhysicIST(self):
        # short cut to launch only this test from here
        super(SgeRunnerTestCase, self).testPhysicIST()


@skip('Not Yet implemented')
class SgeSshRunnerTestCase(SAGARunnerTestCase):
    def setUp(self):
        self.adaptor = SGEOverSSHAdaptor(init_params=dict(host='lamarck',
                                                          user_id='lefort',
                                                          user_pass='lrdj_@81'))
        super(SgeSshRunnerTestCase, self).setUp()
