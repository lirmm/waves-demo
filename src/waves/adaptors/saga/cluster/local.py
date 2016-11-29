from __future__ import unicode_literals

from django.conf import settings

from waves.adaptors.saga.shell.local import ShellJobAdaptor

__group__ = "Local"


class ClusterJobAdaptor(ShellJobAdaptor):
    """
    Encapsulate some of Saga-python adaptors for common cluster calculation devices onto WAVES adaptor logic
    """
    name = 'Local cluster adaptor'
    #: For cluster based remote runners, set up default cluster job queue (if any)
    queue = ''
    #: List of currently implemented remote cluster schemes
    protocol = settings.WAVES_CLUSTER_ADAPTORS

    @property
    def init_params(self):
        """ Base init_params for Cluster JobAdaptor """
        base = super(ClusterJobAdaptor, self).init_params
        base.update(dict(queue=self.queue, protocol=self.protocol))
        return base

    def _job_description(self, job):
        jd = super(ClusterJobAdaptor, self)._job_description(job)
        jd.update(dict(queue=self.queue))
        return jd