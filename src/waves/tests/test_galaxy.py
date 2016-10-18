from __future__ import unicode_literals
import logging
import time
import os
import bioblend
import utils.galaxy_util as test_util
from django.conf import settings
import waves.const as const
import waves.settings
from waves.tests.utils import get_sample_dir
from django.test import override_settings
from waves.tests.test_runner import TestBaseJobRunner
from waves.models import Runner, Service, Job, JobOutput, JobInput
from waves.adaptors.api.galaxy import GalaxyJobAdaptor, GalaxyWorkFlowAdaptor

logger = logging.getLogger(__name__)


@test_util.skip_unless_galaxy()
class GalaxyRunnerTestCase(TestBaseJobRunner):
    def setUp(self):
        self.adaptor = GalaxyJobAdaptor(init_params={'host': waves.settings.WAVES_TEST_GALAXY_URL,
                                                     'port': waves.settings.WAVES_TEST_GALAXY_PORT,
                                                     'app_key': waves.settings.WAVES_TEST_GALAXY_API_KEY})
        super(GalaxyRunnerTestCase, self).setUp()
        # ShortCut for adaptor GI
        self.gi = self.adaptor.connect()

    @classmethod
    def setUpClass(cls):
        super(GalaxyRunnerTestCase, cls).setUpClass()

    def test_list_galaxy_tools(self):
        """
        Test listing of available galaxy tools
        Returns:

        """
        # print 'test', self.adaptor
        tools = self.adaptor.importer(for_runner=self.runner_model).list_all_remote_services()
        logger.debug('Retrieved tools %s', tools)
        self.assertGreater(len(tools), 0)

    def _import_tool_from_service(self, remote_tool_id, service=None):
        importer = self.runner_model.get_importer()
        return importer.import_remote_service(remote_tool_id=remote_tool_id)

    @test_util.skip_unless_tool("fastme")
    def test_import_FastME(self):
        from shutil import copyfile
        tool_client = bioblend.galaxy.objects.client.ObjToolClient(self.gi)
        fast_me = tool_client.list(name='FastME')
        self.assertTrue(len(fast_me) > 0)
        self.service = self._import_tool_from_service(fast_me[0].id)
        self.adaptor.remote_tool_id = fast_me[0].id
        # TODO remove this (moved in testFastMe function)
        self.current_job = Job.objects.create(service=self.service, title="TestFastMe Galaxy")
        source_file = os.path.join(get_sample_dir(), 'fast_me', 'fastme-dna.phy')
        copyfile(source_file, os.path.join(self.current_job.working_dir, 'fastme-dna.phy'))
        self.current_job.job_inputs.add(
            JobInput.objects.create(job=self.current_job, name="input_data",
                                    srv_input=self.service.default_submission.service_inputs.get(name='input'),
                                    value='fastme-dna.phy'))
        self.current_job.job_inputs.add(
            JobInput.objects.create(job=self.current_job, name="dna", type=waves.const.TYPE_TEXT,
                                    param_type=waves.const.OPT_TYPE_VALUATED,
                                    value='J'))
        # associated outputs
        for srv_output in self.service.service_outputs.all():
            self.current_job.job_outputs.add(JobOutput.objects.create(job=self.current_job, srv_output=srv_output,
                                                                      may_be_empty=True))
        self.runJobWorkflow()

    @test_util.skip_unless_tool("physic_ist")
    def test_import_Physic_IST(self):
        tool_client = bioblend.galaxy.objects.client.ObjToolClient(self.gi)
        physic_ist = tool_client.list(name='Compute supertrees')
        self.assertTrue(len(physic_ist) > 0)
        self._import_tool_from_service(physic_ist[0].id)

    def test_job_retrieve(self):
        # TODO complete test
        job_client = bioblend.galaxy.jobs.JobsClient(self.gi.gi)
        jobs = job_client.get_jobs()
        for job in jobs[0:1]:
            details = job_client.show_job(job_id=job['id'], full_details=True)

    def test_galaxy(self):
        # TODO complete test
        import waves.adaptors.api.galaxy
        try:

            all_galaxy_jobs = Job.objects \
                .get_created_job(extra_filter={'service__run_on__clazz__name': 'waves.adaptors.api.GalaxyJobAdaptor'})

            for job in all_galaxy_jobs:
                self.assertIsInstance(job, Job)
                job.make_job_dirs()

                logger.debug(u'Job retrieved:' + str(job))
                service = job.service
                runner = self.adaptor
                run_params = job.service.run_params()
                runner.remote_tool_id = run_params['remote_tool_id']
                logger.debug(u'Runner retrieved: %s %s ', runner, runner.init_params)
                logger.debug(runner._dump_config())
                self.assertIsInstance(runner, waves.adaptors.galaxy.GalaxyJobAdaptor)
                runner.connect()
                self.assertTrue(runner._ready())
                runner.prepare_job(job)
                logger.debug('Related history id %s', job.remote_history_id)
                self.assertTrue(job.status == const.JOB_PREPARED)
                runner.remote_tool_id = service.service_run_params.get(param__name='remote_tool_id').value
                job_id = runner.run_job(job)
                self.assertTrue(job.status == const.JOB_QUEUED)
                status = runner.job_status(job)
                while status < const.JOB_COMPLETED:
                    status = runner.job_status(job)
                    time.sleep(2)
                    logger.info(u'const. : ' + str(job.get_status_display()))
                self.assertTrue(job.status == const.JOB_COMPLETED)
                results = runner.job_results(job)
                self.assertEquals(len(results), len(job.job_outputs.all()))
                for job_output in results:
                    self.assertIsInstance(job_output, JobOutput)
                    logger.debug('Current result %s ', job_output.file_path)
                    self.assertTrue(os.path.isfile(str(job_output.file_path)))
        except Runner.DoesNotExist, Service.DoesNotExist:
            logger.warn(u'Object does not exists')

    def tearDown(self):
        """
        Delete created histories on remote Galaxy server after classic tearDown
        Returns:
            None
        """
        super(GalaxyRunnerTestCase, self).tearDown()
        for history in self.gi.histories.list():
            logger.debug('Deleting history %s:%s ', history.name, history.id)
            self.gi.histories.delete(history.id, purge=self.gi.gi.config.get_config()['allow_user_dataset_purge'])


@test_util.skip_unless_galaxy()
class GalaxyWorkFlowRunnerTestCase(TestBaseJobRunner):
    def setUp(self):
        self.adaptor = GalaxyWorkFlowAdaptor(init_params={'host': waves.settings.WAVES_TEST_GALAXY_URL,
                                                          'port': waves.settings.WAVES_TEST_GALAXY_PORT,
                                                          'app_key': waves.settings.WAVES_TEST_GALAXY_API_KEY})
        super(GalaxyWorkFlowRunnerTestCase, self).setUp()

    @property
    def importer(self):
        return self.adaptor.importer(for_runner=self.runner_model)

    def test_list_galaxy_workflow(self):
        services = self.importer.list_all_remote_services()
        self.assertGreaterEqual(len(services), 0)

    def test_import_new_workflow(self):
        services = self.importer.list_all_remote_services()
        for remote_service in services[0:1]:
            self.importer.import_remote_service(remote_tool_id=remote_service[0])

    def test_update_existing_workflow(self):
        service = Service.objects.filter(run_on__clazz__name='waves.adaptors.GalaxyWorkFlowAdaptor')
        self.assertGreaterEqual(len(service), 0)
        for updated in service[0:1]:
            # just try for the the first one
            remote_tool_param = updated.service_run_params.get(param__name='remote_tool_id')
            logger.debug('Remote too id for service %s : %s', updated, remote_tool_param.value)
            self.importer.import_remote_service(remote_tool_id=remote_tool_param.value)
