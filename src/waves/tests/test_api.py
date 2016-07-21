from __future__ import unicode_literals
import logging

from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase

from waves.models import Job, Service
from waves.tests import WavesBaseTestCase
from waves.api.urls import router
import waves.const

logger = logging.getLogger(__name__)
AuthModel = get_user_model()


def _create_test_file(path, index):
    import os
    full_path = os.path.join(settings.WAVES_DATA_ROOT, '_' + str(index) + '_' + path)
    f = open(full_path, 'w')
    f.write('sample content for input file %s' % ('_' + str(index) + '_' + path))
    f.close()
    f = open(full_path, 'rb')
    return f


class WavesAPITestCase(APITestCase, WavesBaseTestCase):
    def setUp(self):
        super(WavesAPITestCase, self).setUp()
        self.group_admin = Group.objects.get(name=settings.WAVES_GROUP_ADMIN)
        self.super_user = AuthModel.objects.create(email='superadmin@waves.fr',
                                                   is_superuser=True)
        self.super_user.groups.add(self.group_admin)
        self.admin_user = AuthModel.objects.create(email='admin@waves.fr',
                                                   is_staff=True)
        self.admin_user.groups.add(self.group_admin)
        self.api_user = AuthModel.objects.create(email="api@waves.fr",
                                                 is_staff=False,
                                                 is_superuser=False)
        self.api_user.profile.registered_for_api = True
        self.api_user.save()
        self.api_user.groups.add(Group.objects.get(name=settings.WAVES_GROUP_API))
        self.users = {'api': self.api_user, 'admin': self.admin_user, 'root': self.super_user}

    def tearDown(self):
        super(WavesAPITestCase, self).tearDown()

    def testSetUp(self):
        self.assertTrue(self.super_user.is_superuser)
        self.assertTrue(self.group_admin in self.super_user.groups.all())
        self.assertIsNotNone(self.super_user.profile.api_key)
        self.assertTrue(self.admin_user.is_staff)
        self.assertTrue(self.group_admin in self.admin_user.groups.all())
        self.assertFalse(self.api_user.is_staff)

    def _dataUser(self, user='api', initial={}):
        initial.update({'api_key': self.users[user].profile.api_key})
        logger.debug('Request Data: %s', initial)
        return initial


class ServiceTests(WavesAPITestCase):
    def test_api_key(self):
        api_root = self.client.get(reverse('api-root'), data=self._dataUser('root'))
        self.assertEqual(api_root.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(api_root.data), 3)

    def test_list_services(self):
        tool_list = self.client.get(reverse('servicetool-list'),
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
            reverse('servicetoolcategory-list'), data=self._dataUser())
        self.assertEqual(category_list.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(category_list.data), 2)
        for category in category_list.data:
            self.assertGreaterEqual(category['tools'], 1)


class JobTests(WavesAPITestCase):
    def test_create_job(self):
        """
        Ensure for any service, we can create a job according to retrieved parameters
        """
        import random
        import string
        logger.debug('Retrieving servicetool-list from ' + reverse('servicetool-list'))
        tool_list = self.client.get(reverse('servicetool-list'), data=self._dataUser())
        self.assertEqual(tool_list.status_code, status.HTTP_200_OK)
        for servicetool in tool_list.data:
            logger.debug('Creating job submission for %s %s', servicetool['name'], str(servicetool['version']))
            # for each servicetool retrieve inputs
            self.assertIsNotNone(servicetool['url'])
            detail = self.client.get(servicetool['url'], data=self._dataUser())
            logger.debug('Details data: %s', detail)
            tool_data = detail.data
            service_id = tool_data['id']
            logger.debug('Retrieved service %s ', detail.data['id'])
            input_datas = {
                'service': detail.data['id'],
            }
            i = 0
            for job_input in tool_data['inputs']:
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
                input_datas[job_input['name']] = input_data

            logger.debug('Data posted %s', input_datas)

            response = self.client.post('/api/jobs/',
                                        data=self._dataUser(initial=input_datas),
                                        format='multipart')
            logger.debug(response)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

            job = Job.objects.all().order_by('-created').first()
            service = Service.objects.get(pk=service_id)
            self.assertEquals(len(job.job_outputs.all()), len(service.service_outputs.all()))

    def test_update_job(self):
        pass

    def test_delete_job(self):
        pass

    def test_job_error(self):
        pass

    def test_get_status(self):
        pass

    def testPhysicIST(self):
        detail = self.client.get(reverse('servicetool-detail',
                                         kwargs={'api_name': 'physic_ist'}),
                                 data=self._dataUser(initial={'api_name': 'physic_ist'}))
        jobs_params = self._loadServiceJobsParams(api_name='physic_ist')
        input_service = {
            'service': self.service.pk,
        }
        for submitted_input in jobs_params:
            logger.debug('Data posted %s', submitted_input)
            submitted_input.update(input_service)
            response = self.client.post('/api/jobs/',
                                        data=self._dataUser(initial=submitted_input),
                                        format='multipart')
            logger.debug(response)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
