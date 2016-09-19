from __future__ import unicode_literals

import logging
import json
import os
import sys
from os.path import join, dirname, isfile, realpath

from django.conf import settings
from django.test import TestCase, override_settings
from django.core.exceptions import ObjectDoesNotExist
import waves.settings
from waves.models import Service
from utils import get_sample_dir

logger = logging.getLogger(__name__)
# waves.settings.WAVES_DATA_ROOT = str(os.path.join(waves.settings.WAVES_TEST_DIR, 'data'))
# waves.settings.WAVES_SAMPLE_DIR = str(os.path.join(waves.settings.WAVES_TEST_DIR, 'data', 'sample'))
# waves.settings.WAVES_JOB_DIR = str(os.path.join(waves.settings.WAVES_TEST_DIR, 'data', 'jobs'))


@override_settings(
    MEDIA_ROOT=os.path.join(dirname(settings.BASE_DIR), 'tests', 'media'),
    WAVES_DATA_ROOT=str(os.path.join(dirname(settings.BASE_DIR), 'tests', 'data')),
    WAVES_SAMPLE_DIR=str(os.path.join(dirname(os.path.abspath(__file__)), 'data', 'sample')),
    WAVES_JOB_DIR=str(os.path.join(dirname(settings.BASE_DIR), 'tests', 'data', 'jobs'))
)
class WavesBaseTestCase(TestCase):
    current_result = None
    # fixtures = ['test_init.json']

    @classmethod
    def setUpClass(cls):
        super(WavesBaseTestCase, cls).setUpClass()
        logger.info('MEDIA_ROOT: %s', settings.MEDIA_ROOT)
        logger.info('WAVES_DATA_ROOT: %s', settings.WAVES_DATA_ROOT)
        logger.info('WAVES_JOB_DIR: %s', settings.WAVES_JOB_DIR)
        logger.info('WAVES_SAMPLE_DIR: %s', settings.WAVES_SAMPLE_DIR)
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
        jobs_submitted_input = []
        try:
            self.service = Service.objects.get(api_name=api_name)
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
                for key in job_params['params']:
                    submitted_input.update({key: job_params['params'][key]})
                jobs_submitted_input.append(submitted_input)
        except ObjectDoesNotExist as e:
            logger.error(e.message)
            self.skipTest("No physic_ist service available")
        return jobs_submitted_input
