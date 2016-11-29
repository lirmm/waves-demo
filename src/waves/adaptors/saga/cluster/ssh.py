from __future__ import unicode_literals

from waves.adaptors.saga.cluster.local import ClusterJobAdaptor
from waves.adaptors.saga.shell.ssh import SshUserPassJobAdaptor, SshKeyJobAdaptor

__group__ = 'SSH'

class SshUserPassClusterJobAdaptor(ClusterJobAdaptor, SshUserPassJobAdaptor):
    """
    Cluster calls over SSH with user password
    """
    name = 'SSH remote cluster adaptor (user/pass)'
    pass


class SshKeyClusterJobAdaptor(ClusterJobAdaptor, SshKeyJobAdaptor):
    """
    Cluster calls over SSH with private key and pass phrase
    """
    name = 'SSH remote cluster adaptor (key)'
    pass
