"""
Saga-python based SGE job adaptor
"""
from __future__ import unicode_literals

from waves.adaptors.saga.shell.local import ShellJobAdaptor

__all__ = [str('SGEJobAdaptor')]


class SGEJobAdaptor(ShellJobAdaptor):
    """
    Locally available SGE cluster
    .. deprecated::
        Prefer use of waves.adaptors.saga_adaptor.ClusterJobAdaptor with SunGridEngine protocol

    """
    name = 'SGE dedicated local cluster adaptor (Deprecated)'

    queue = 'mainqueue'
    protocol = 'sge'

    @property
    def init_params(self):
        """
        Return SGE cluster init params
        :return:
        """
        base = super(SGEJobAdaptor, self).init_params
        base.update(dict(queue=self.queue))
        return base

    def _job_description(self, job):
        jd = super(SGEJobAdaptor, self)._job_description(job)
        jd.update(dict(queue=self.queue))
        return jd
