from __future__ import unicode_literals

import waves.settings
from waves.adaptors.local import ShellJobAdaptor
import logging

logger = logging.getLogger(__name__)


class SGEJobAdaptor(ShellJobAdaptor):
    """
    Locally available SGE cluster
    """
    queue = waves.settings.WAVES_SGE_CELL
    _protocol = 'sge'

    @property
    def init_params(self):
        base = super(SGEJobAdaptor, self).init_params
        base.update(dict(queue=self.queue))
        return base

    def _job_description(self, job):
        jd = super(SGEJobAdaptor, self)._job_description(job)
        jd.update(dict(queue=self.queue))
        return jd


