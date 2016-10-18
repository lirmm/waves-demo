from __future__ import unicode_literals

from collections import namedtuple



"""
from waves.adaptors.galaxy import GalaxyJobAdaptor, GalaxyWorkFlowAdaptor
from waves.adaptors.runner import JobRunnerAdaptor
from waves.adaptors.local import ShellJobAdaptor
from waves.adaptors.sge import SGEJobAdaptor
from waves.adaptors.api.compphy import CompPhyApiAdaptor
from waves.adaptors.ssh import SshJobAdaptor, SshKeyJobAdaptor, SshUserPassJobAdaptor, SGEOverSSHAdaptor

__all__ = ['SGEJobAdaptor', 'GalaxyJobAdaptor', 'GalaxyWorkFlowAdaptor', 'ShellJobAdaptor',
           'CompPhyApiAdaptor']

"""
__all__ = ['adaptors.sge.SGEJobAdaptor', 'adaptors.galaxy.GalaxyJobAdaptor', 'adaptors.galaxy.GalaxyWorkFlowAdaptor',
           'adaptors.local.ShellJobAdaptor', 'adaptors.api.compphy.CompPhyApiAdaptor']
def get_implementation():
    # waves.settings.WAVES_ENABLED_ADAPTORS
    classes_list = []
    from django.utils.module_loading import import_module
    for cls in import_module(__package__).__all__:
        classes_list.append(__package__ + '.' + cls)
    return classes_list

JobRunInfo = namedtuple("JobInfo",
                        """jobId hasExited hasSignal terminatedSignal hasCoreDump
                        wasAborted exitStatus resourceUsage""")
