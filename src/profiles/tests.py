""" Tests profiles """
from __future__ import unicode_literals
from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings
from os.path import join, dirname

# Create your tests here.
from django.urls import reverse
from django.conf import settings
from accounts.views import SignUpView

User = get_user_model()


@override_settings(
    MEDIA_ROOT=join(dirname(settings.BASE_DIR), 'tests', 'media')
)
class ProfileTestCase(TestCase):
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
