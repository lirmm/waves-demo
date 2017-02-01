"""Galaxy Adaptor test cases """
from __future__ import unicode_literals

import logging

from waves.adaptors.importers.dto import Job, JobInput, JobOutput

import waves.tests.utils.galaxy_util as test_util
from adaptors import working_dir, sample_file
from waves import tests as settings
from waves.adaptors.core.api.galaxy import GalaxyJobAdaptor
from waves.tests import TestBaseJobRunner

logger = logging.getLogger(__name__)


@test_util.skip_unless_galaxy()
class GalaxyRunnerTestCase(TestBaseJobRunner):
    def setUp(self):
        self.adaptor = GalaxyJobAdaptor(init_params={'host': settings.WAVES_TEST_GALAXY_URL,
                                                     'port': settings.WAVES_TEST_GALAXY_PORT,
                                                     'app_key': settings.WAVES_TEST_GALAXY_API_KEY})
        super(GalaxyRunnerTestCase, self).setUp()

    def test_import_galaxy_tools(self):
        """
        Test listing of available galaxy tools
        """
        importer = self.adaptor.importer
        tools = importer.list_services()
        self.assertGreater(len(tools), 0)
        services = []
        n_tools = 0
        n_cat = 0
        for cat in tools:
            logger.info('Category %s:', cat[0])
            n_cat += 1
            for tool in cat[1]:
                n_tools += 1
                logger.info('Import service %s:%s', tool.name, tool.remote_service_id)
                importer.import_service(tool.remote_service_id)
                if n_tools > 2:
                    break

        # control services import
        for service in services:
            self.assertGreater(len(service.inputs), 0)
        logger.info('Imported %i services in %i categories ', n_tools, n_cat)

    @test_util.skip_unless_tool('MAF_To_Fasta1')
    def test_maf_to_fasta(self):
        import uuid
        import shutil
        from os import mkdir
        from os.path import join
        importer = self.adaptor.importer
        service = importer.import_service('MAF_To_Fasta1')
        self.adaptor.tool_id = service.remote_service_id
        input_data = service.inputs[0]
        slug = uuid.uuid4()
        job_dir = join(working_dir, str(slug))
        job = Job(title='Job for %s' % service.name, service=service,
                  slug=slug, working_dir=job_dir)
        input1 = JobInput.init_from_service(input_data)
        input1.value = 'sample.maf'
        source_file = sample_file('maff_to_fasta/sample.maf')
        mkdir(job.working_dir)
        shutil.copy(source_file, job.working_dir)
        job.inputs.append(input1)
        output = JobOutput.init_from_service(service.outputs[0])
        output.value = service.outputs[0].name
        job.outputs.append(output)
        self.current_job = job
        self.runJobWorkflow()
        with open(sample_file('maff_to_fasta/expected.fasta'), 'r') as expect, \
                open(join(job.working_dir, job.outputs[0].file_path), 'r') as result:
            self.assertEqual(expect.read().strip(), result.read().strip())


"""
# TODO finish the job for workflows
@test_util.skip_unless_galaxy()
class GalaxyWorkFlowRunnerTestCase(TestJobRunner):
    def setUp(self):
        self.adaptor = GalaxyWorkFlowAdaptor(init_params={'host': waves.settings.WAVES_TEST_GALAXY_URL,
                                                          'port': waves.settings.WAVES_TEST_GALAXY_PORT,
                                                          'app_key': waves.settings.WAVES_TEST_GALAXY_API_KEY})
        super(GalaxyWorkFlowRunnerTestCase, self).setUp()

    @property
    def importer(self):
        return self.adaptor.importer(for_runner=self.runner_model)

    def test_list_galaxy_workflow(self):
        services = self.importer.list_services()
        if len(services) > 0:
            self.assertGreaterEqual(len(services), 0)
        else:
            self.skipTest("No remote workflows ")

    def test_import_new_workflow(self):
        workflows = self.importer.list_services()
        if len(workflows) > 0:
            for remote_service in workflows:
                self.importer.import_service(remote_tool_id=remote_service[0])
        else:
            self.skipTest("No remote workflows ")

    @unittest.skip('WorkFlow not really available for now')
    def test_update_existing_workflow(self):
        service = Service.objects.filter(run_on__clazz='waves.adaptors.core.api.galaxy.GalaxyWorkFlowAdaptor')
        self.assertGreaterEqual(len(service), 0)
        for updated in service[0:1]:
            # just try for the the first one
            remote_tool_param = updated.service_run_params.get(param__name='remote_tool_id')
            logger.debug('Remote too id for service %s : %s', updated, remote_tool_param.value)
            self.importer.import_service(remote_tool_id=remote_tool_param.value)
"""