from __future__ import unicode_literals

import logging
import json
import os


from django.conf import settings
from django.test import TestCase, override_settings
from django.core.exceptions import ObjectDoesNotExist

from waves.models import Service

logger = logging.getLogger(__name__)


@override_settings(
    MEDIA_ROOT=os.path.join(settings.BASE_DIR, 'test_media'),
    WAVES_DATA_ROOT=os.path.join(settings.WAVES_BASEDIR, 'test_data'),
    WAVES_JOB_DIR=os.path.join(settings.WAVES_BASEDIR, 'test_data', 'jobs'),
    WAVES_SAMPLE_DIR=os.path.join(settings.WAVES_BASEDIR, 'test_data', 'sample'),
)
class WavesBaseTestCase(TestCase):
    current_result = None
    fixtures = ['test_init.json']

    @classmethod
    def setUpClass(cls):
        super(WavesBaseTestCase, cls).setUpClass()
        logger.info('WAVES_GALAXY_URL: %s', settings.WAVES_GALAXY_URL)
        logger.info('WAVES_GALAXY_API_KEY: %s', settings.WAVES_GALAXY_API_KEY)
        logger.info('WAVES_GALAXY_PORT: %s', settings.WAVES_GALAXY_PORT)
        logger.info('MEDIA_ROOT: %s', settings.MEDIA_ROOT)
        logger.info('WAVES_DATA_ROOT: %s', settings.WAVES_DATA_ROOT)
        logger.info('WAVES_JOB_DIR: %s', settings.WAVES_JOB_DIR)
        logger.info('WAVES_SAMPLE_DIR: %s', settings.WAVES_SAMPLE_DIR)

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
        jobs_submitted_input = []
        try:
            self.service = Service.objects.get(api_name=api_name)
            logger.debug('Physic_IST service %s %s ', self.service.name, self.service.version)
            logger.debug('Sample dir %s ', self.service.sample_dir)
            with open(os.path.join(self.service.sample_dir, 'runs.json'), 'r') as run_params:
                job_parameters = json.load(run_params)
            self.assertIsInstance(job_parameters, object)
            submitted_input = {}
            for job_params in job_parameters['runs']:
                logger.debug('job_params: %s %s ', job_params.__class__, job_params)
                submitted_input['title'] = job_params['title']
                # All files inputs
                for key in job_params['inputs']:
                    with open(os.path.join(self.service.sample_dir, job_params['inputs'][key])) as f:
                        submitted_input.update({key: f.read()})
                for key in job_params['params']:
                    submitted_input.update({key: job_params['params'][key]})
                jobs_submitted_input.append(submitted_input)
        except ObjectDoesNotExist as e:
            logger.error(e.message)
            self.skipTest("No physic_ist service available")
        return jobs_submitted_input

