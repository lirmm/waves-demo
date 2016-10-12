from __future__ import unicode_literals

import saga
import os
import logging
import time
from unittest import skip

from django.conf import settings

import waves.const
import waves.tests.utils.shell_util as test_util
from waves.tests.test_runner import TestBaseJobRunner, Service, sample_job
from waves.adaptors import ShellJobAdaptor, SshUserPassJobAdaptor, SGEJobAdaptor
from waves.models import Job, JobInput, JobOutput
from waves.adaptors.ssh import SGEOverSSHAdaptor
from waves.managers.servicejobs import ServiceJobManager
from waves.tests.utils import get_sample_dir
import waves.settings

logger = logging.getLogger(__name__)


class SAGARunnerTestCase(TestBaseJobRunner):
    def setUp(self):
        try:
            getattr(self, 'adaptor')
        except AttributeError:
            self.adaptor = ShellJobAdaptor()
        super(SAGARunnerTestCase, self).setUp()

    def _testBasicSagaLocalJob(self):
        try:
            # Create a job service object that represent the local machine.
            # The keyword 'fork://' in the url scheme triggers the 'shell' adaptor
            # which can execute jobs on the local machine as well as on a remote
            # machine via "ssh://hostname".
            ctx = saga.Context('UserPass')
            ctx.user_id = "lefort"
            ctx.user_pass = 'lrdj_@81'
            # ctx.user_cert = '$HOME/.ssh/id_rsa'
            # ctx.user_key = '$HOME/.ssh/id_rsa.pub'
            ses = saga.Session()
            ses.add_context(ctx)
            js = saga.job.Service("sge+ssh://wilkins")

            # describe our job
            jd = saga.job.Description()

            # Next, we describe the job we want to run. A complete set of job
            # description attributes can be found in the API documentation.
            jd.environment = {'MYOUTPUT': '"Hello from SAGA"'}
            jd.executable = '/bin/echo'
            jd.arguments = ['$MYOUTPUT']
            jd.output = "mysagajob.stdout"
            jd.error = "mysagajob.stderr"
            jd.working_directory = '/tmp/'
            jd.queue = 'all.q'

            # Create a new job from the job description. The initial state of
            # the job is 'New'.
            myjob = js.create_job(jd)

            # Check our job's id and state
            logger.debug("Job ID    : %s" % (myjob.id))
            logger.debug("Job State : %s" % (myjob.state))
            logger.debug("\n...starting job...\n")

            # Now we can start our job.
            myjob.run()

            logger.debug("Job ID    : %s" % (myjob.id))
            logger.debug("Job State : %s" % (myjob.state))
            logger.debug("\n...waiting for job...\n")
            # wait for the job to either finish or fail
            myjob.wait()

            logger.debug("Job State : %s" % (myjob.state))
            logger.debug("Exitcode  : %s" % (myjob.exit_code))
            self.assertTrue(True)
        except saga.SagaException as ex:
            # Catch all saga exceptions
            logger.error("An exception occured: (%s) %s " % (ex.type, (str(ex))))
            logger.error(" \n*** Backtrace:\n %s" % ex.traceback)

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
            logger.debug('Job command line %s', self.current_job.command_line)
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
            logger.info(u'Current job state (%i) : %s ', ix, self.current_job.get_status_display())
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
