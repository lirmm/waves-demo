from __future__ import unicode_literals

import logging
import saga

import waves.const
import waves.tests.utils.shell_util as test_util
from waves.tests.test_runner import TestBaseJobRunner, Service
from waves.runners import ShellJobRunner, SshUserPassJobRunner, SGEOverSSHRunner, SGEJobRunner


logger = logging.getLogger(__name__)


class LocalRunnerTestCase(TestBaseJobRunner):

    def setUp(self):
        self.runner = ShellJobRunner()
        super(LocalRunnerTestCase, self).setUp()

    @classmethod
    def setUpClass(cls):
        super(LocalRunnerTestCase, cls).setUpClass()
        # class level sample data

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

    def testHelloWorld(self):
        self._prepare_hello_world()
        self.runJobWorkflow()
        self.assertEqual(self.job.status, waves.const.JOB_TERMINATED)

    @test_util.skip_unless_tool('physic_ist')
    def testPhysicIST(self):
        jobs_params = self._loadServiceJobsParams(api_name='physic_ist')
        self.runner.command = 'physic_ist'
        for submitted_input in jobs_params:
            job = Service.objects.create_new_job(service=self.service, submitted_inputs=submitted_input)
            logger.debug('Job command line %s', job.command_line)
            self.runJobWorkflow(job)


class SshRunnerTestCase(LocalRunnerTestCase):
    def setUp(self):
        self.runner = SshUserPassJobRunner(init_params=dict(user_id='marc',
                                                            user_pass='Projet2501LIRMM:-)'))
        super(LocalRunnerTestCase, self).setUp()


class SgeRunnerTestCase(LocalRunnerTestCase):
    def setUp(self):
        self.runner = SGEJobRunner(init_params=dict(queue='mainqueue'))
        super(SgeRunnerTestCase, self).setUp()


class SgeSshRunnerTestCase(LocalRunnerTestCase):
    def setUp(self):
        self.runner = SGEOverSSHRunner(init_params=dict(host='lamarck',
                                                        user_id='lefort',
                                                        user_pass='lrdj_@81'))
        super(LocalRunnerTestCase, self).setUp()

