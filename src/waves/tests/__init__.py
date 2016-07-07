from __future__ import unicode_literals

from os.path import join
import logging

from django.conf import settings
from django.test import TestCase, override_settings

logger = logging.getLogger(__name__)


@override_settings(
    MEDIA_ROOT=join(settings.BASE_DIR, 'test_media'),
    WAVES_DATA_ROOT=join(settings.WAVES_BASEDIR, 'test_data'),
    WAVES_JOB_DIR=join(settings.WAVES_BASEDIR, 'test_data', 'jobs'),
    WAVES_SAMPLE_DIR=join(settings.WAVES_BASEDIR, 'test_data', 'sample'),
)
class WavesBaseTestCase(TestCase):

    current_result = None

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

    def run(self, result=None):
        self.current_result = result
        super(WavesBaseTestCase, self).run(result)

    def tearDown(self):
        super(WavesBaseTestCase, self).tearDown()

