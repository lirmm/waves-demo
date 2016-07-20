from __future__ import unicode_literals

import logging
import saga

import waves.const
import waves.tests.utils.shell_util as test_util
from waves.tests.test_runner import *
from waves.runners import ShellJobRunner

logger = logging.getLogger(__name__)


class LocalSagaAdapterTestCase(TestBaseJobRunner):

    def setUp(self):
        self.runner = ShellJobRunner()
        super(LocalSagaAdapterTestCase, self).setUp()

    @classmethod
    def setUpClass(cls):
        super(LocalSagaAdapterTestCase, cls).setUpClass()
        # class level sample data

    def testBasicSagaLocalJob(self):
        try:
            # Create a job service object that represent the local machine.
            # The keyword 'fork://' in the url scheme triggers the 'shell' adaptor
            # which can execute jobs on the local machine as well as on a remote
            # machine via "ssh://hostname".
            js = saga.job.Service("fork://localhost")

            # describe our job
            jd = saga.job.Description()

            # Next, we describe the job we want to run. A complete set of job
            # description attributes can be found in the API documentation.
            jd.environment = {'MYOUTPUT': '"Hello from SAGA"'}
            jd.executable = '/bin/echo'
            jd.arguments = ['$MYOUTPUT']
            jd.output = "mysagajob.stdout"
            jd.error = "mysagajob.stderr"

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

            logger.degug("Job State : %s" % (myjob.state))
            logger.degug("Exitcode  : %s" % (myjob.exit_code))
            self.assertTrue(True)
        except saga.SagaException as ex:
            # Catch all saga exceptions
            logger.error("An exception occured: (%s) %s " % (ex.type, (str(ex))))
            logger.error(" \n*** Backtrace:\n %s" % ex.traceback)

    def testHelloWorld(self):
        self._prepare_hello_world()
        self.runJobWorkflow()
        self.assertEqual(self.job.status, waves.const.JOB_TERMINATED)

    @test_util.skip_unless_tool('physic_ist')
    def testPhysicIST(self):
        jobs = self._preparePhysicISTJobs()
        self.runner.command = 'physic_ist'
        for job in jobs:
            logger.debug('Job command line %s', job.command_line)
            self.runJobWorkflow(job)
            self.assertGreaterEqual(job.status, waves.const.JOB_COMPLETED)
