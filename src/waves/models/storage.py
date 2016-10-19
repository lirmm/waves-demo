from __future__ import unicode_literals

from django.core.files.storage import FileSystemStorage
import waves.settings


class WavesStorage(FileSystemStorage):
    def __init__(self):
        self.location = waves.settings.WAVES_DATA_ROOT
        self.directory_permissions_mode = 0o775
        self.file_permissions_mode = 0o775

waves_storage = WavesStorage
