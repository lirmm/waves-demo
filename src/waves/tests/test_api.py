from __future__ import unicode_literals

import logging
from urlparse import urlparse

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase

import waves.const
from waves.models import Job
from waves.tests.base import WavesBaseTestCase
import waves.settings

logger = logging.getLogger(__name__)
AuthModel = get_user_model()


def _create_test_file(path, index):
    import os
    full_path = os.path.join(waves.settings.WAVES_DATA_ROOT, 'jobs', '_' + str(index) + '_' + path)
    f = open(full_path, 'w')
    f.write('sample content for input file %s' % ('_' + str(index) + '_' + path))
    f.close()
    f = open(full_path, 'rb')
    return f


class WavesAPITestCase(APITestCase, WavesBaseTestCase):
    def setUp(self):
        super(WavesAPITestCase, self).setUp()
        self.super_user = AuthModel.objects.create(email='superadmin@waves.fr',
                                                   is_superuser=True)
        self.admin_user = AuthModel.objects.create(email='admin@waves.fr',
                                                   is_staff=True)
        self.api_user = AuthModel.objects.create(email="api@waves.fr",
                                                 is_staff=False,
                                                 is_superuser=False,
                                                 is_active=True)
        self.api_user.profile.registered_for_api = True
        self.api_user.save()
        self.users = {'api': self.api_user, 'admin': self.admin_user, 'root': self.super_user}

    def tearDown(self):
        super(WavesAPITestCase, self).tearDown()

    def testSetUp(self):
        self.assertTrue(self.super_user.is_superuser)
        self.assertIsNotNone(self.super_user.profile.api_key)
        self.assertTrue(self.admin_user.is_staff)
        self.assertFalse(self.api_user.is_staff)

    def _dataUser(self, user='api', initial={}):
        initial.update({'api_key': self.users[user].profile.api_key})
        return initial


class ServiceTests(WavesAPITestCase):
    def test_api_key(self):
        api_root = self.client.get(reverse('waves:api-root'), data=self._dataUser('root'))
        self.assertEqual(api_root.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(api_root.data), 3)

    def test_list_services(self):
        tool_list = self.client.get(reverse('waves:waves-services-list'),
                                    data=self._dataUser('admin'),
                                    format='json')
        self.assertEqual(tool_list.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(tool_list)
        for servicetool in tool_list.data:
            self.assertIsNotNone(servicetool['url'])
            detail = self.client.get(servicetool['url'],
                                     data=self._dataUser('admin'), )
            self.assertEqual(detail.status_code, status.HTTP_200_OK)
            tool_data = detail.data
            self.assertIsNotNone(tool_data['name'])

    def test_list_categories(self):
        category_list = self.client.get(
            reverse('waves:waves-services-category-list'), data=self._dataUser())
        self.assertEqual(category_list.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(category_list.data), 0)
        for category in category_list.data:
            self.assertGreaterEqual(category['tools'], 1)

    def testHTTPMethods(self):
        pass


class JobTests(WavesAPITestCase):
    def test_create_job(self):
        """
        Ensure for any service, we can create a job according to retrieved parameters
        """
        import random
        import string
        logger.debug('Retrieving service-list from ' + reverse('waves:waves-services-list'))
        tool_list = self.client.get(reverse('waves:waves-services-list'), data=self._dataUser())
        self.assertEqual(tool_list.status_code, status.HTTP_200_OK)
        self.assertGreater(len(tool_list.data), 0)
        for servicetool in tool_list.data:
            logger.debug('Creating job submission for %s %s', servicetool['name'], str(servicetool['version']))
            # for each servicetool retrieve inputs
            self.assertIsNotNone(servicetool['url'])
            detail = self.client.get(servicetool['url'], data=self._dataUser())
            # logger.debug('Details data: %s', detail)
            tool_data = detail.data
            self.assertTrue('submissions' in tool_data)
            i = 0
            input_datas = {}
            submissions = tool_data.get('submissions')
            for submission in submissions:
                # print submission['label']
                for job_input in submission['inputs']:
                    if job_input['type'] == waves.const.TYPE_FILE:
                        i += 1
                        input_data = _create_test_file(job_input['name'], i)
                        # input_datas[job_input['name']] = input_data.name
                        logger.debug('file input %s', input_data)
                    elif job_input['type'] == waves.const.TYPE_INTEGER:
                        input_data = int(random.randint(0, 199))
                        logger.debug('number input%s', input_data)
                    elif job_input['type'] == waves.const.TYPE_FLOAT:
                        input_data = int(random.randint(0, 199))
                        logger.debug('number input%s', input_data)
                    elif job_input['type'] == waves.const.TYPE_BOOLEAN:
                        input_data = random.randrange(100) < 50
                    elif job_input['type'] == 'text':
                        input_data = ''.join(random.sample(string.letters, 15))
                        # input_datas[job_input['name']] = input_data
                        logger.debug('text input %s', input_data)
                    else:
                        input_data = ''.join(random.sample(string.letters, 15))
                        logger.warn('default ???? %s %s', input_data, job_input['type'])
                    input_datas[job_input['name']] = input_data

                logger.debug('Data posted %s', input_datas)
                logger.debug('To => %s', submission['submission_uri'])
                o = urlparse(servicetool['url'])
                path = o.path.split('/')
                response = self.client.post(submission['submission_uri'],
                                            data=self._dataUser(initial=input_datas),
                                            format='multipart')
                logger.debug(response)
                self.assertEqual(response.status_code, status.HTTP_201_CREATED)
                job = Job.objects.all().order_by('-created').first()
                logger.debug(job)

    def test_update_job(self):
        pass

    def test_delete_job(self):
        pass

    def test_job_error(self):
        pass

    def test_get_status(self):
        pass

    def testPhysicIST(self):
        jobs_params = self._loadServiceJobsParams(api_name='physic_ist')
        for submitted_input in jobs_params:
            logger.debug('Data posted %s', submitted_input)
            url_post = self.client.get(reverse('waves:waves-services-detail',
                                               kwargs={'api_name': 'physic_ist'}),
                                       data=self._dataUser())
            response = self.client.post(url_post.data['default_submission_uri'],
                                        data=self._dataUser(initial=submitted_input),
                                        format='multipart')
            logger.debug(response)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            job_details = self.client.get(reverse('waves:waves-jobs-detail',
                                                  kwargs={'slug': response.data['slug']}),
                                          data=self._dataUser())
            self.assertEqual(job_details.status_code, status.HTTP_200_OK)
            job = Job.objects.get(slug=response.data['slug'])
            self.assertIsInstance(job, Job)
            self.assertEqual(job.status, waves.const.JOB_CREATED)

    def testMissingParam(self):
        jobs_params = self._loadServiceJobsParams(api_name='physic_ist')
        submitted_input = jobs_params[0]
        submitted_input.pop('s')
        logger.debug('Data posted %s', submitted_input)
        response = self.client.get(reverse('waves:waves-services-detail',
                                           kwargs={'api_name': 'physic_ist'}),
                                   data=self._dataUser())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post(response.data['default_submission_uri'],
                                    data=self._dataUser(initial=submitted_input),
                                    format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        logger.info(response)
