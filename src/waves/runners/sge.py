from __future__ import unicode_literals
import logging

from django.conf import settings

from waves.runners.ssh import *

logger = logging.getLogger(__name__)


class SGEJobRunner(ShellJobRunner):
    """
    Locally available SGE cluster
    """
    queue = settings.WAVES_SGE_CELL
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


class SGEOverSSHRunner(SGEJobRunner, SshUserPassJobRunner):
    _protocol = 'sge+ssh'

    @property
    def init_params(self):
        base = super(SGEJobRunner, self).init_params
        base.update(super(SshJobRunner, self).init_params)
        return base

    def _job_description(self, job):

        dir_name = 'sftp://' + self.host + "/$HOME/sge_runs/"
        work_dir = saga.filesystem.Directory(dir_name, saga.filesystem.READ,
                                                    self.session)
        jd = super(SGEJobRunner, self)._job_description(job)
        jd.update(dict(queue=self.queue, working_directory='/$HOME/sge_runs/'))
        return jd
