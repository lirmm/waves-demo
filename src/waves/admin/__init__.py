""" Models admin packages """
from django.conf import settings

from waves.admin.jobs import *
from waves.admin.runners import *
from waves.admin.services import *
from waves.admin.submissions import SubmissionOutputInline, ExitCodeInline, SampleDependentInputInline, \
    FileInputSampleInline
if 'jet' in settings.INSTALLED_APPS:
    from waves.admin.submissions_jet import ServiceSubmissionAdmin
else:
    from waves.admin.submissions_std import SubmissionAdmin

from waves.admin.inputs import *
from waves.admin.admin import *