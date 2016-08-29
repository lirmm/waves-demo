from __future__ import unicode_literals

import saga
import waves.settings
from waves.runners.local import ShellJobRunner
import logging

logger = logging.getLogger(__name__)


class SGEJobRunner(ShellJobRunner):
    """
    Locally available SGE cluster
    """
    queue = waves.settings.WAVES_SGE_CELL
    _protocol = 'sge'

    @property
    def init_params(self):
        base = super(SGEJobRunner, self).init_params
        base.update(dict(queue=self.queue))
        return base

    def _job_description(self, job):
        jd = super(SGEJobRunner, self)._job_description(job)
        jd.update(dict(queue=self.queue))
        return jd


