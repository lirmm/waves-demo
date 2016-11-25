"""
WAVES runner adaptor module
"""
from __future__ import unicode_literals

__author__ = "Marc Chakiachvili <marc.chakiachvili@lirmm.fr>"
__version__ = "1.0"

from .api.compphy import *
from .api.galaxy import *
from .saga import *

__all__ = ['ShellJobAdaptor', 'ClusterJobAdaptor', 'CompPhyApiAdaptor',
           "GalaxyJobAdaptor", "GalaxyWorkFlowAdaptor", "SshKeyClusterJobAdaptor",
           "SshUserPassJobAdaptor", 'SshKeyJobAdaptor', 'SshUserPassClusterJobAdaptor']


def get_implementation():
    classes_list = []
    from django.utils.module_loading import import_module, import_string
    sub_modules = ['api.galaxy', 'api.compphy', 'saga']
    for sub in sub_modules:
        # print sub
        sub_module = import_module(__package__ + '.' + sub)
        for cls in sub_module.__all__:
            clazz = import_string(sub_module.__name__ + '.' + cls)
            classes_list.append(clazz)
    return classes_list

CURRENT_IMPLEMENTATION = get_implementation
