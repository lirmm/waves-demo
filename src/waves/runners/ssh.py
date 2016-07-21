from __future__ import unicode_literals

import saga
from local import ShellJobRunner


class SshJobRunner(ShellJobRunner):
    port = 22
    _saga_protocol = 'ssh'

    @property
    def init_params(self):
        params = super(SshJobRunner, self).init_params
        params.update(dict(host=self.host,
                           port=self.port))
        return params

    @property
    def context(self):
        return saga.Context('ssh')

    def _prepare_job(self, job):
        super(SshJobRunner, self)._prepare_job(job)
        # TODO manage File transfer (uploads)

    def _job_results(self, job):
        return super(SshJobRunner, self)._job_results(job)


class SshKeyJobRunner(SshJobRunner):
    private_key = None
    public_key = None
    pass_phrase = None

    @property
    def init_params(self):
        params = super(SshKeyJobRunner, self).init_params
        params.update(dict(private_key=self.private_key,
                           pass_phrase=self.pass_phrase,
                           public_key=self.public_key))
        return params


class SshUserPassJobRunner(SshJobRunner):
    user_id = None
    user_pass = None

    @property
    def init_params(self):
        params = super(SshUserPassJobRunner, self).init_params
        params.update(dict(user_id=self.user_id,
                           user_pass=self.user_pass))
        return params

    @property
    def context(self):
        ctx = saga.Context('UserPass')
        ctx.user_id = self.user_id
        ctx.user_pass = self.user_pass
        return ctx
