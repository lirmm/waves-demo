"""
WSGI config for waves_services project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""
from __future__ import unicode_literals

import os
# Load saga before anything related to Django: avoid user warning about loggers
import saga

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "waves_demo.settings.production")

application = get_wsgi_application()
