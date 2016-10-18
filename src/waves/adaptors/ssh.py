from __future__ import unicode_literals

import saga

from local import ShellJobAdaptor


class SshJobAdaptor(ShellJobAdaptor):
    # TODO add implementation to change ssh port capability
    port = 22
    _protocol = 'ssh'
    # Remote basedir
    basedir = '/tmp'

    @property
    def init_params(self):
        params = super(SshJobAdaptor, self).init_params
        params.update(dict(host=self.host,
                           port=self.port,
                           basedir=self.basedir))
        return params

    @property
    def context(self):
        return saga.Context('ssh')

    def _prepare_job(self, job):
        super(SshJobAdaptor, self)._prepare_job(job)
        # TODO manage File transfer (uploads)

    def _job_results(self, job):
        return super(SshJobAdaptor, self)._job_results(job)
        # TODO manage File transfer (downloads)


class SshKeyJobAdaptor(SshJobAdaptor):
    """
    SSH remote job control, over ssh, authenticated with private key and pass phrase
    """
    private_key = '$HOME/.ssh/id_rsa'
    public_key = '$HOME/.ssh/id_rsa.pub'
    pass_phrase = None

    @property
    def init_params(self):
        params = super(SshKeyJobAdaptor, self).init_params
        params.update(dict(private_key=self.private_key,
                           pass_phrase=self.pass_phrase,
                           public_key=self.public_key))
        return params

    @property
    def context(self):
        ctx = super(SshJobAdaptor, self).context
        ctx.user_cert = self.private_key
        ctx.user_key = self.public_key
        ctx.user_pass = self.pass_phrase
        return ctx


class SshUserPassJobAdaptor(SshJobAdaptor):
    """
    SSH remote job control, over ssh, authenticated with classic user_id and password credentials
    """
    user_id = None
    user_pass = None

    @property
    def init_params(self):
        params = super(SshUserPassJobAdaptor, self).init_params
        params.update(dict(user_id=self.user_id,
                           user_pass=self.user_pass))
        return params

    @property
    def context(self):
        ctx = saga.Context('UserPass')
        ctx.user_id = self.user_id
        ctx.user_pass = self.user_pass
        return ctx


