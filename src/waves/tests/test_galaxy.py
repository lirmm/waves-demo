from __future__ import unicode_literals
import logging
import time
import os
import bioblend

import utils.galaxy_util as test_util
import waves.const as const
from waves.tests.test_runner import TestBaseJobRunner
from waves.models import Runner, Service, Job, JobOutput
from waves.runners.galaxy import GalaxyJobRunner, GalaxyWorkFlowRunner

logger = logging.getLogger(__name__)


@test_util.skip_unless_galaxy()
class GalaxyRunnerTestCase(TestBaseJobRunner):
    # This is fixture:
    # fields: {name: GalaxyTestRunner, clazz: waves.runners.GalaxyJobRunner}
    # model: waves.models.Runner
    # pk: 1
    # fixtures = ['users', 'test_services']

    def setUp(self):
        self.runner = GalaxyJobRunner()
        super(GalaxyRunnerTestCase, self).setUp()
        self.gi = bioblend.galaxy.objects.galaxy_instance.GalaxyInstance(url=self.runner.complete_url,
                                                                     api_key=self.runner.app_key)

    def test_list_galaxy_tools(self):
        """
        Test listing of available galaxy tools
        Returns:

        """
        tools = self.runner_model.importer().list_all_remote_services()
        logger.debug('Retrieved tools %s', tools)
        self.assertGreater(len(tools), 0)

    def _import_tool_from_service(self, remote_tool_id):
        importer = self.runner_model.importer()
        importer.import_remote_service(remote_tool_id=remote_tool_id)

    @test_util.skip_unless_tool("fastme")
    def test_import_FastME(self):
        tool_client = bioblend.galaxy.objects.client.ObjToolClient(self.gi)
        fast_me = tool_client.list(name='FastME')
        self.assertTrue(len(fast_me) > 0)
        self._import_tool_from_service(fast_me[0].id)

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
        import waves.runners.galaxy
        try:

            all_galaxy_jobs = Job.objects \
                .get_created_job(extra_filter={'service__run_on__clazz': 'waves.runners.GalaxyJobRunner'})

            for job in all_galaxy_jobs:
                self.assertIsInstance(job, Job)
                job.make_job_dirs()

                logger.debug(u'Job retrieved:' + str(job))
                service = job.service
                runner = self.runner
                run_params = job.service.run_params()
                runner.remote_tool_id = run_params['remote_tool_id']
                logger.debug(u'Runner retrieved: %s %s ', runner, runner.init_params)
                logger.debug(runner._dump_config())
                self.assertIsInstance(runner, waves.runners.galaxy.GalaxyJobRunner)
                runner.connect()
                self.assertTrue(runner._ready())
                runner.prepare_job(job)
                logger.debug('Related history id %s', job.eav.galaxy_history_id)
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
        self.runner = GalaxyWorkFlowRunner()
        super(GalaxyWorkFlowRunnerTestCase, self).setUp()
        self.gi = bioblend.galaxy.objects.galaxy_instance.GalaxyInstance(url=self.runner.complete_url,
                                                                     api_key=self.runner.app_key)

    def test_list_galaxy_workflow(self):
        importer = self.runner_model.importer()
        services = importer.list_all_remote_services()
        self.assertGreater(len(services), 0)

    def test_import_new_workflow(self):
        importer = self.runner_model.importer()
        services = importer.list_all_remote_services()
        for remote_service in services[0:1]:
            importer.import_remote_service(remote_tool_id=remote_service[0])

    def test_update_existing_workflow(self):
        service = Service.objects.filter(run_on__clazz='waves.runners.GalaxyWorkFlowRunner')
        if service.count() == 0:
            self.fail('Unable to test update workflow, since there is none in db')
        for updated in service[0:1]:
            # just try for the the first one
            importer = self.runner_model.importer(for_service=updated)
            remote_tool_param = updated.service_run_params.get(param__name='remote_tool_id')
            logger.debug('Remote too id for service %s : %s', updated, remote_tool_param.value)
            importer.import_remote_service(remote_tool_id=remote_tool_param.value)


