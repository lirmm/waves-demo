from __future__ import unicode_literals

import saga
from saga import SagaException

from waves.adaptors.exceptions import AdaptorJobException
from waves.utils.encrypt import EncryptedValue
from .local import ShellJobAdaptor

__group__ = 'SSH'


class SshJobAdaptor(ShellJobAdaptor):
    """
    Saga-python base SSH adaptor (Shell remote calls)
    Run locally on remote host job command
    """
    #: remote user_id for ssh connexion
    user_id = ''
    #: saga protocol
    protocol = 'ssh'
    #: remote ssh port
    port = '22'
    #: Remote absolute basedir
    basedir = '/tmp'

    @property
    def saga_host(self):
        """ Construct saga-python host scheme str """
        if self.protocol != 'ssh':
            saga_host = '%s+ssh://%s' % (self.protocol, self.host)
        else:
            saga_host = super(SshJobAdaptor, self).saga_host
        return '%s:%s' % (saga_host, self.port)

    @property
    def init_params(self):
        """ SSH saga-python required init parameters """
        params = super(SshJobAdaptor, self).init_params
        params.update(dict(user_id=self.user_id,
                           host=self.host,
                           port=self.port,
                           basedir=self.basedir,
                           protocol=self.protocol))
        return params

    def _job_description(self, job):
        """
        Job description for saga-python library
        :param job:
        :return: a dictionary with data set up according to job
        """
        return dict(working_directory=self.remote_work_dir(job).get_url().path,
                    executable=self.command,
                    arguments=job.command.get_command_line_element_list(job.job_inputs.all()),
                    output=job.stdout,
                    error=job.stderr)

    @property
    def remote_dir(self):
        """ Construct remote ssh host remote dir (uploads) """
        return "sftp://%s%s" % (self.host, self.basedir)

    @property
    def context(self):
        """ Configure SSH saga context properties """
        ctx = saga.Context('ssh')
        ctx.remote_port = self.port
        return ctx

    def remote_work_dir(self, job, mode=saga.filesystem.READ):
        """ Setup remote host working dir """
        return saga.filesystem.Directory('%s/%s' % (self.remote_dir, str(job.slug)), mode,
                                         session=self.session)

    def _prepare_job(self, job):
        """
        Prepare job on remote host
          - Create remote working dir
          - Upload job input files
        """
        super(SshJobAdaptor, self)._prepare_job(job)
        try:
            work_dir = self.remote_work_dir(job, saga.filesystem.CREATE_PARENTS)
            for input_file in job.input_files.all():
                wrapper = saga.filesystem.File('file://localhost/%s' % input_file.file_path)
                wrapper.copy(work_dir.get_url())
        except SagaException as exc:
            raise AdaptorJobException(exc)

    def _job_results(self, job):
        """
        Download all files located in remote job working dir
        :param job: the Job to retrieve file for
        :return: None
        """
        try:
            work_dir = self.remote_work_dir(job)
            for remote_file in work_dir.list('*'):
                work_dir.copy(remote_file, 'file://localhost/%s/' % job.working_dir)
            return super(SshJobAdaptor, self)._job_results(job)
        except SagaException as exc:
            return AdaptorJobException(exc)


class SshKeyJobAdaptor(SshJobAdaptor):
    """
    SSH remote job control, over ssh, authenticated with private key and pass phrase
    """
    name = 'SSH remote adaptor (key)'
    private_key = '$HOME/.ssh/id_rsa'
    public_key = '$HOME/.ssh/id_rsa.pub'
    crypt_pass_phrase = None

    @property
    def init_params(self):
        """ Update init params with expected ones from SSH private/public key login """
        params = super(SshKeyJobAdaptor, self).init_params
        params.update(dict(private_key=self.private_key,
                           crypt_pass_phrase=self.crypt_pass_phrase,
                           public_key=self.public_key))
        return params

    @property
    def context(self):
        """ Setup saga context to connect over ssh using private/public key with pass phrase """
        ctx = super(SshKeyJobAdaptor, self).context
        ctx.user_id = self.user_id
        ctx.user_cert = self.private_key
        ctx.user_key = self.public_key
        ctx.user_pass = EncryptedValue.decrypt(self.crypt_pass_phrase)
        return ctx


class SshUserPassJobAdaptor(SshJobAdaptor):
    """
    SSH remote job control, over ssh, authenticated with classic user_id and password credentials
    """
    name = 'SSH remote adaptor (user/pass)'
    crypt_user_pass = None

    @property
    def init_params(self):
        """ Update Adaptor init_params with SSH user/pass login expected params"""
        params = super(SshUserPassJobAdaptor, self).init_params
        params.update(dict(crypt_user_pass=self.crypt_user_pass))
        return params

    @property
    def context(self):
        """ Setup saga context to connect over ssh with UserPass protocol """
        ctx = saga.Context('UserPass')
        ctx.user_id = self.user_id
        ctx.user_pass = EncryptedValue.decrypt(self.crypt_user_pass)
        return ctx