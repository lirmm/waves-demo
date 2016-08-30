#!/usr/bin/env python
import os
import sys
from django.conf import settings

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "waves_services.settings.cli")
    from django.core.management import execute_from_command_line
    print settings.DATABASES['default']
    execute_from_command_line(sys.argv)
