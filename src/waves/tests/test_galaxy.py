"""Galaxy Adaptor test cases """
from __future__ import unicode_literals

import logging
import unittest

from django.conf import settings
from waves.adaptors.api.galaxy import GalaxyJobAdaptor, GalaxyWorkFlowAdaptor
from waves.adaptors.exceptions import AdaptorConnectException

import utils.galaxy_util as test_util
import waves.settings
from waves.models import Service
from waves.tests.test_runner import TestBaseJobRunner

logger = logging.getLogger(__name__)


@test_util.skip_unless_galaxy()
class GalaxyRunnerTestCase(TestBaseJobRunner):
    def setUp(self):
        self.adaptor = GalaxyJobAdaptor(init_params={'host': settings.WAVES_TEST_GALAXY_URL,
                                                     'port': settings.WAVES_TEST_GALAXY_PORT,
                                                     'app_key': settings.WAVES_TEST_GALAXY_API_KEY})
        super(GalaxyRunnerTestCase, self).setUp()
        # ShortCut for adaptor GI
        try:
            self.gi = self.adaptor.connect()
        except AdaptorConnectException:
            self.skipTest('Unable to connect to remote')
        else:
            logger.info('Adaptor config: %s' % self.adaptor.dump_config())

    @classmethod
    def setUpClass(cls):
        super(GalaxyRunnerTestCase, cls).setUpClass()

    def test_list_galaxy_tools(self):
        """
        Test listing of available galaxy tools
        """
        tools = self.adaptor.importer.list_services()
        self.assertGreater(len(tools), 0)

    @test_util.skip_unless_tool("MAF_To_Fasta1")
    def test_import_tool(self):
        service = self.adaptor.importer.import_remote_service("MAF_To_Fasta1", self.runner_model)

        self.assertIsNotNone(service)
        self.assertIsNotNone(service.submissions)
        self.assertGreater(service.submissions.first().submission_inputs.count(), 0)

    @test_util.skip_unless_tool("toolshed.g2.bx.psu.edu/repos/rnateam/mafft/rbc_mafft/7.221.1")
    def test_import_mafft(self):
        service = self.adaptor.importer.import_remote_service(
            "toolshed.g2.bx.psu.edu/repos/rnateam/mafft/rbc_mafft/7.221.1", self.runner_model)
        self.assertIsNotNone(service)

    def tearDown(self):
        """
        Delete created histories on remote Galaxy server after classic tearDown
        Returns:
            None
        """
        super(GalaxyRunnerTestCase, self).tearDown()
        if not settings.WAVES_DEBUG_GALAXY:
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
        services = self.importer.list_services()
        if len(services) > 0:
            self.assertGreaterEqual(len(services), 0)
        else:
            self.skipTest("No remote workflows ")

    def test_import_new_workflow(self):
        workflows = self.importer.list_services()
        if len(workflows) > 0:
            for remote_service in workflows:
                self.importer.import_remote_service(remote_tool_id=remote_service[0])
        else:
            self.skipTest("No remote workflows ")

    @unittest.skip('WorkFlow not really available for now')
    def test_update_existing_workflow(self):
        service = Service.objects.filter(runner__runner='waves.adaptors.api.galaxy.GalaxyWorkFlowAdaptor')
        self.assertGreaterEqual(len(service), 0)
        for updated in service[0:1]:
            # just try for the the first one
            remote_tool_param = updated.srv_run_params.get(name='remote_tool_id')
            logger.debug('Remote too id for service %s : %s', updated, remote_tool_param.value)
            self.importer.import_remote_service(remote_tool_id=remote_tool_param.value)
