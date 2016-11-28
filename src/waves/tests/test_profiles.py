from __future__ import unicode_literals

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from waves.tests.base import WavesBaseTestCase
from django.test import override_settings
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.core import mail
from waves.views.accounts import SignUpView


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
    data_register = {
        'email': 'test@test.com',
        'name': 'Register full name',
        'password1': 'pass1',
        'password2': 'pass1',
        'country': 'FR',
        'institution': 'LIRMM',
        'phone': '3369999999',
        'comment': 'Any comment',
        'tos': True
    }

    def test_profiles_created(self):
        u = User.objects.create_user(email="dummy@example.com")
        self.assertIsNotNone(u.profile)
        u.profile.registered_for_api = True
        u.save()
        self.assertIsNotNone(u.profile.api_key)

    @override_settings(
        WAVES_REGISTRATION_ALLOWED=False,
    )
    def testRegistrationDisallowed(self):
        url = reverse('waves:registration_register')
        r = self.client.get(url)
        self.assertRedirects(r, reverse('waves:registration_disallowed'))

    @override_settings(
        WAVES_REGISTRATION_ALLOWED=True,
    )
    def testRegistrationAllowed(self):
        url = reverse('waves:registration_register')
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        r = self.client.post(url, data=self.data_register)
        self.assertRedirects(r, reverse('waves:registration_complete'))
        # check if mail is sent
        self.assertEqual(len(mail.outbox), 1)
        user = User.objects.get(email='test@test.com')
        self.assertIsNotNone(user)
        self.assertFalse(user.is_active)
        reg_view = SignUpView()
        activation_url = reverse('waves:registration_activate',
                                 kwargs=dict(activation_key=reg_view.get_activation_key(user)))
        r = self.client.get(activation_url)
        self.assertRedirects(r, reverse('waves:registration_activation_complete'))
        user = User.objects.get(email='test@test.com')
        self.assertTrue(user.is_active)
