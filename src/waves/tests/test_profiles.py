from __future__ import unicode_literals

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from waves.tests.base import WavesBaseTestCase
import waves.const


class PageOpenTestCase(TestCase):
    def test_home_page_exists(self):
        url = reverse('waves:home')
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)

    def test_about_page_exists(self):
        url = reverse('waves:about')
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)


User = get_user_model()


class ProfileTestCase(WavesBaseTestCase):
    def test_profiles_created(self):
        u = User.objects.create_user(email="dummy@example.com")
        self.assertIsNotNone(u.profile)
        u.profile.registered_for_api = True
        u.save()
        self.assertIsNotNone(u.profile.api_key)


