from __future__ import unicode_literals
from local import ShellJobRunner


class SshJobRunner(ShellJobRunner):

    host = '127.0.0.1'
    ssh_key = None
    port = 22

    @property
    def init_params(self):
        return super(SshJobRunner, self).init_params().update(dict(host=self.host,
                                                                   port=self.port,
                                                                   ssh_key=self.ssh_key))
