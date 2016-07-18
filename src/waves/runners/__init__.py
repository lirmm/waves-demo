from __future__ import unicode_literals

import logging
from collections import namedtuple

from django.conf import settings

from waves.runners.drmaa import DRMAAJobRunner
from waves.runners.galaxy import GalaxyJobRunner, GalaxyWorkFlowRunner
from waves.runners.local import ShellJobRunner
from waves.runners.runner import JobRunner
from waves.runners.sge import SGEJobRunner
from waves.runners.ssh import SshJobRunner

__all__ = ['SGEJobRunner', 'GalaxyJobRunner', 'GalaxyWorkFlowRunner', 'ShellJobRunner']

if settings.DEBUG:
    from waves.runners.mock import MockJobRunner
    __all__ += ['MockJobRunner']


logger = logging.getLogger(__name__)


def get_implementation():
    classes_list = []
    from django.utils.module_loading import import_module
    for cls in import_module(__package__).__all__:
        classes_list.append(__package__ + '.' + cls)
    return classes_list

JobRunInfo = namedtuple("JobInfo",
                        """jobId hasExited hasSignal terminatedSignal hasCoreDump
                        wasAborted exitStatus resourceUsage""")
