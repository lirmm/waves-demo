from __future__ import unicode_literals

from django.core.files.storage import FileSystemStorage
import waves.settings

waves_storage = FileSystemStorage(location=waves.settings.WAVES_DATA_ROOT,
                                  directory_permissions_mode=0o775,
                                  file_permissions_mode=0o775)
