#!/usr/bin/env python
from __future__ import  unicode_literals

import os
import sys
# Load saga before anything related to Django: avoid user warning about loggers
import saga

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "waves_demo.settings.production")

    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
