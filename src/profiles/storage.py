""" WAVES Files storage engine parameters """
from __future__ import unicode_literals

from django.core.files.storage import FileSystemStorage
from django.conf import settings


class ProfileStorage(FileSystemStorage):
    """ Profile FileSystem Storage engine """

    def __init__(self):
        super(ProfileStorage, self).__init__(location=settings.MEDIA_ROOT,
                                             directory_permissions_mode=0o775,
                                             file_permissions_mode=0o775)

profile_storage = ProfileStorage()


def profile_directory(instance, filename):
    """ User Profile images directory """
    return 'profile/{0}/{1}'.format(instance.slug, filename)