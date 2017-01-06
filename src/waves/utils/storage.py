""" WAVES Files storage engine parameters """
from __future__ import unicode_literals

from django.core.files.storage import FileSystemStorage
import waves.settings


class WavesStorage(FileSystemStorage):
    """ Waves FileSystem Storage engine """
    def __init__(self):
        super(WavesStorage, self).__init__(location=waves.settings.WAVES_DATA_ROOT,
                                           directory_permissions_mode=0o775,
                                           file_permissions_mode=0o775)


def file_sample_directory(instance, filename):
    """ Submission file sample directory upload pattern """
    return 'sample/{0}/{1}/{2}'.format(str(instance.submission.service.api_name), str(instance.submission.slug), filename)


def job_file_directory(instance, filename):
    """ Submitted job input files """
    return 'jobs/{0}/{1}'.format(str(instance.job.slug), filename)


def profile_directory(instance, filename):
    """ User Profile images directory """
    return 'profile/{0}/{1}'.format(instance.slug, filename)

waves_storage = WavesStorage()


