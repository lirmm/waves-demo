""" SAGA based WAVES adaptors"""
from __future__ import unicode_literals

from .shell.local import ShellJobAdaptor
from .shell.ssh import SshUserPassJobAdaptor, SshKeyJobAdaptor
from .cluster.ssh import SshKeyClusterJobAdaptor, SshUserPassClusterJobAdaptor
from .cluster.local import ClusterJobAdaptor

__all__ = [str('ShellJobAdaptor'),
           str('SshUserPassJobAdaptor'),
           str('SshKeyJobAdaptor'),
           str('ClusterJobAdaptor'),
           str('SshUserPassClusterJobAdaptor'),
           str('SshKeyClusterJobAdaptor')]

__group__ = "Saga"
__author__ = "Marc Chakiachvili"
__version__ = '0.1.0'


