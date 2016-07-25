from __future__ import unicode_literals

import logging
import os
import time

from django.conf import settings

import waves.const
import waves.tests.utils.shell_util as test_util
from waves.tests.test_runner import *
from waves.runners import SGEJobRunner
from waves.models import JobOutput, JobInput, RunnerParam, Service

logger = logging.getLogger(__name__)


class SGEAdapterTestCase(TestBaseJobRunner):
    """
    DRMAA API compliant test cases
    """

    def setUp(self):
        self.runner = SGEJobRunner()
        super(SGEAdapterTestCase, self).setUp()

    def tearDown(self):
        super(SGEAdapterTestCase, self).tearDown()
        # logger.debug('Session count %s ', self.runner._connector.session_count)
        # self.runner.disconnect()

    @test_util.skip_unless_tool('services/hello_world.sh')
    def testHelloWorld(self):
        self._prepare_hello_world()
        self.runJobWorkflow()
        self.assertEqual(self.job.status, waves.const.JOB_TERMINATED)

    def _prepare_hello_world(self):
        self.runner.command = os.path.join(test_util.get_sample_dir(), 'services/hello_world.sh')
        JobInput.objects.create(job=self.job, name="TestInput1", value='Test Input 1',
                                param_type=waves.const.OPT_TYPE_POSIX, type=waves.const.TYPE_TEXT)
        JobInput.objects.create(job=self.job, name="TestInput2", value='Test Input 2',
                                param_type=waves.const.OPT_TYPE_POSIX, type=waves.const.TYPE_TEXT)

        JobOutput.objects.create(job=self.job, value='hello_world_output.txt', name="Output file", type="txt")

    @test_util.skip_unless_tool('cp')
    def testSimpleCP(self):
        self.runner.command = 'cp'
        JobInput.objects.create(job=self.job, name='Input_file', type=waves.const.TYPE_FILE,
                                param_type=waves.const.OPT_TYPE_POSIX,
                                value=os.path.join(settings.WAVES_SAMPLE_DIR, 'sample_tree.nhx'))
        JobInput.objects.create(job=self.job, name='Destination', type=waves.const.TYPE_TEXT,
                                param_type=waves.const.OPT_TYPE_POSIX,
                                value=self.job.output_dir)
        JobOutput.objects.create(job=self.job, name='', label="Copied File",
                                 value='sample_tree.nhx')

        self.runJobWorkflow()

    @test_util.skip_unless_tool('services/hello_world.sh')
    def testCancelJob(self):
        self._prepare_hello_world()
        self.runner.prepare_job(self.job)
        self.assertEqual(self.job.status, waves.const.JOB_PREPARED)
        self.runner.run_job(self.job)
        self.assertEqual(self.job.status, waves.const.JOB_QUEUED)
        for ix in range(30):
            job_state = self.runner.job_status(self.job)
            logger.info(u'Current job state (%i) : %s ', ix, self.job.get_status_display())
            if job_state > waves.const.JOB_QUEUED:
                self.runner.cancel_job(self.job)
                break
            else:
                time.sleep(1)
        self.assertEqual(self.job.status, waves.const.JOB_CANCELLED)

    @test_util.skip_unless_tool('fastme')
    def testFastME(self):
        import drmaa.session
        self.runner.command = 'fastme'
        JobInput.objects.create(job=self.job, name="input_data", type=waves.const.TYPE_FILE,
                                param_type=waves.const.OPT_TYPE_VALUATED,
                                value=os.path.join(settings.WAVES_SAMPLE_DIR, 'fast_me', 'nucleic.phy'))
        JobInput.objects.create(job=self.job, name="dna", type=waves.const.TYPE_TEXT,
                                param_type=waves.const.OPT_TYPE_VALUATED,
                                value='J')
        output_tree = JobInput.objects.create(job=self.job, name="output_tree", type=waves.const.TYPE_TEXT,
                                              param_type=waves.const.OPT_TYPE_VALUATED,
                                              value='output_tree.txt')
        output_matrix = JobInput.objects.create(job=self.job, name="output_matrix", type=waves.const.TYPE_TEXT,
                                                param_type=waves.const.OPT_TYPE_VALUATED,
                                                value='output_matrix.txt')
        output_info = JobInput.objects.create(job=self.job, name='output_info', type=waves.const.TYPE_TEXT,
                                              param_type=waves.const.OPT_TYPE_VALUATED,
                                              value="output_info.txt")
        # associated outputs
        JobOutput.objects.create(job=self.job, name='Inferred tree file',
                                 value=output_tree.value)
        JobOutput.objects.create(job=self.job, name="Computed matrix",
                                 value=output_matrix.value)
        JobOutput.objects.create(job=self.job, name="Output Info",
                                 value=output_info.value)
        self.runJobWorkflow()
        self.assertGreaterEqual(self.job.status, waves.const.JOB_COMPLETED)
        # Test retrieve job_run details twice
        job_details = self.runner.job_run_details(self.job)
        self.assertIsInstance(job_details, drmaa.session.JobInfo)

    @test_util.skip_unless_tool('physic_ist')
    def testPhysicIST(self):
        jobs_params = self._loadServiceJobsParams(api_name='physic_ist')
        self.runner.command = 'physic_ist'
        for submitted_input in jobs_params:
            job = Service.objects.create_new_job(service=self.service, submitted_inputs=submitted_input)
            logger.debug('Job command line %s', job.command_line)
            self.runJobWorkflow(job)
