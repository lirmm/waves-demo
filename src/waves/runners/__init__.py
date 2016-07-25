from __future__ import unicode_literals

from collections import namedtuple

from waves.runners.galaxy import GalaxyJobRunner, GalaxyWorkFlowRunner
from waves.runners.runner import JobRunner
from waves.runners.sge import *
from waves.runners.ssh import *

__all__ = ['SGEJobRunner', 'GalaxyJobRunner', 'GalaxyWorkFlowRunner', 'ShellJobRunner', 'SshKeyJobRunner',
           'SshUserPassJobRunner', 'SGEJobRunner', 'SGEOverSSHRunner']

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
