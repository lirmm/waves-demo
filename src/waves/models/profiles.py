from __future__ import unicode_literals
from django.conf import settings
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django_countries.fields import CountryField
from waves.models.base import SlugAble
import logging
logger = logging.getLogger(__name__)


def profile_directory(instance, filename):
    return 'profile/{0}/{1}'.format(instance.slug, filename)


@python_2_unicode_compatible
class APIProfile(SlugAble):
    class Meta:
        unique_together = ('user', 'api_key')

    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                primary_key=True, related_name='profile',
                                on_delete=models.CASCADE)
    picture = models.ImageField('Profile picture',
                                upload_to=profile_directory,
                                null=True,
                                blank=True,
                                help_text='Users\'s avatar')
    registered_for_api = models.BooleanField('Registered for api use', default=False,
                                             help_text='Register for REST API use')
    api_key = models.CharField('Api key',
                               max_length=255,
                               null=True,
                               blank=True,
                               unique=True,
                               help_text='User\'s api access key')
    institution = models.CharField('Institution',
                                   null=True,
                                   max_length=255,
                                   blank=False,
                                   help_text='User\'s laboratory')
    country = CountryField(blank=True,
                           blank_label='Select country',
                           null=True,
                           help_text='User\'s country')
    phone = models.CharField('Phone',
                             max_length=12,
                             blank=True,
                             null=True,
                             help_text='User\'s phone number')
    comment = models.TextField('Comments',
                               blank=True,
                               null=True,
                               help_text='User\'s comment')
    ip = models.GenericIPAddressField('Restricted IP address',
                                      null=True,
                                      blank=True,
                                      help_text='User\'s restricted IP')
    banned = models.BooleanField('Banned (abuse)', default=False)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.user.is_staff or self.user.is_superuser:
            self.registered_for_api = True
        super(APIProfile, self).save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return "{}".format(self.user)
