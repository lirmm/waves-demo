"""
Saga-python based SGE job adaptor
"""
from __future__ import unicode_literals

import saga

from waves.adaptors.local import ShellJobAdaptor
from waves.adaptors.ssh import SshUserPassJobAdaptor, SshJobAdaptor


class SGEJobAdaptor(ShellJobAdaptor):
    """
    Locally available SGE cluster
    """
    queue = 'all.q'
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


class SGEOverSSHAdaptor(SGEJobAdaptor, SshUserPassJobAdaptor):
    _protocol = 'sge+ssh'

    @property
    def init_params(self):
        base = super(SGEJobAdaptor, self).init_params
        base.update(dict(queue=self.queue, host=self.host))
        return base

    def _job_description(self, job):

        dir_name = 'sftp://' + self.host + "/$HOME/sge_runs/"
        work_dir = saga.filesystem.Directory(dir_name, saga.filesystem.READ,
                                                    self.session)
        jd = super(SGEJobAdaptor, self)._job_description(job)
        jd.update(dict(queue=self.queue, working_directory='/$HOME/sge_runs/'))
        return jd