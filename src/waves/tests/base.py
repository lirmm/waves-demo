"""
Base Waves Unit Test class
"""
from __future__ import unicode_literals
import json
import os
from os.path import dirname
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.test import override_settings, TestCase
from waves.tests.utils import get_sample_dir
import waves.settings
from waves.models.services import ServiceInput, ServiceOutput


@override_settings(
    MEDIA_ROOT=os.path.join(dirname(settings.BASE_DIR), 'tests', 'media'),
    WAVES_JOB_DIR=str(os.path.join(dirname(settings.BASE_DIR), 'tests', 'data', 'jobs')),
    WAVES_DATA_ROOT=str(os.path.join(dirname(settings.BASE_DIR), 'tests', 'data')),
    WAVES_SAMPLE_DIR=str(os.path.join(dirname(settings.BASE_DIR), 'tests', 'data', 'sample'))
)
class WavesBaseTestCase(TestCase):
    current_result = None
    fixtures = ['waves/tests/fixtures/init.json']

    @classmethod
    def setUpClass(cls):
        super(WavesBaseTestCase, cls).setUpClass()
        # copy_sample_dirs()

    def setUp(self):
        super(WavesBaseTestCase, self).setUp()
        self.service = None

    def run(self, result=None):
        self.current_result = result
        super(WavesBaseTestCase, self).run(result)

    def tearDown(self):
        super(WavesBaseTestCase, self).tearDown()

    def _loadServiceJobsParams(self, api_name):
        """
        Test specific phyisic_ist job submission
        Returns:

        """
        import logging
        from waves.models import Service
        logger = logging.getLogger(__name__)
        jobs_submitted_input = []
        try:
            self.service = Service.objects.get(api_name=api_name)
        except ObjectDoesNotExist as e:
            logger.error(e.message)
            # self.skipTest("No physic_ist service available")
            if self.service is None:
                self.service = Service.objects.create(name=api_name, api_name=api_name)
            self.service.api_name = api_name
            self.service.save()
        logger.debug('Physic_IST service %s %s ', self.service.name, self.service.version)
        logger.debug('Sample dir %s %s', get_sample_dir(), self.service.api_name)
        with open(os.path.join(get_sample_dir(), self.service.api_name, 'runs.json'),
                  'r') as run_params:
            job_parameters = json.load(run_params)
        self.assertIsInstance(job_parameters, object)

        for job_params in job_parameters['runs']:
            logger.debug('job_params: %s %s ', job_params.__class__, job_params)
            submitted_input = {'title': job_params['title']}
            # All files inputs
            for key in job_params['inputs']:
                with open(os.path.join(get_sample_dir(), self.service.api_name,
                                       job_params['inputs'][key])) as f:
                    submitted_input.update({key: f.read()})
                # self.service.default_submission.service_inputs.add(ServiceInput.objects.create(ser))
            for key in job_params['params']:
                submitted_input.update({key: job_params['params'][key]})
            jobs_submitted_input.append(submitted_input)
        return jobs_submitted_input
