from __future__ import unicode_literals

from os.path import join

from waves.adaptors.galaxy.tool import GalaxyJobAdaptor as BaseGalaxyJobAdaptor
from waves.wcore.adaptors.cluster import LocalClusterAdaptor as BaseLocalClusterAdaptor
from waves.wcore.adaptors.cluster import SshClusterAdaptor as BaseSshClusterAdaptor
from waves.wcore.adaptors.cluster import SshKeyClusterAdaptor as BaseSshKeyClusterAdaptor
from waves.wcore.adaptors.mocks import MockJobRunnerAdaptor as BaseMockAdaptor
from waves.wcore.adaptors.shell import LocalShellAdaptor as BaseLocalShellAdaptor
from waves.wcore.adaptors.shell import SshKeyShellAdaptor as BaseSshKeyShellAdaptor
from waves.wcore.adaptors.shell import SshShellAdaptor as BaseSshShellAdaptor


class DemoMockConnector():

    def get_job(self, job):
        return job


class WavesDemoAdaptors(BaseMockAdaptor):

    def get_command_line(self, obj):
        if obj.adaptor:
            return "%s %s" % (obj.adaptor.command, obj.command_line)
        else:
            return "Unavailable %s" % obj.command_line

    def _connect(self):
        self.connector = DemoMockConnector()
        self._connected = True

    def __init__(self, command=None, protocol='http', host="localhost", **kwargs):
        super(WavesDemoAdaptors, self).__init__(command, protocol, host, **kwargs)
        self.job = None
        self.command = 'mock_command' or command

    def _job_status(self, job):
        job.logger.info('Mock job status -- Demo -- ')
        job.job_history.create(message='[Fake job status -- Demo -- ] {}'.format(job.slug), status=job.status)
        return super(WavesDemoAdaptors, self)._job_status(job)

    def _run_job(self, job):
        job.logger.info("Entering fake run -- Demo -- ")
        job.job_history.create(message='[Entering fake run -- Demo -- ] {}'.format(job.slug), status=job.status)
        super(WavesDemoAdaptors, self)._run_job(job)
        return job

    def _prepare_job(self, job):
        job.logger.info("Entering fake prepare -- Demo -- ")
        job.job_history.create(message='[Entering fake prepare -- Demo -- ] {}'.format(job.slug), status=job.status)
        return job

    def _job_run_details(self, job):
        return job.default_run_details()

    def _job_results(self, job):
        with open(join(job.working_dir, job.stdout), 'w') as fp:
            fp.write("Executed command on computing infrastructure : {}".format(self.get_command_line(job)))
        return True


class SshShellAdaptor(WavesDemoAdaptors, BaseSshShellAdaptor):
    pass


class LocalClusterAdaptor(WavesDemoAdaptors, BaseLocalClusterAdaptor):
    pass


class SshKeyShellAdaptor(WavesDemoAdaptors, BaseSshKeyShellAdaptor):
    pass


class LocalShellAdaptor(WavesDemoAdaptors, BaseLocalShellAdaptor):
    pass


class SshClusterAdaptor(WavesDemoAdaptors, BaseSshClusterAdaptor):
    pass


class SshKeyClusterAdaptor(WavesDemoAdaptors, BaseSshKeyClusterAdaptor):
    pass


class GalaxyJobAdaptor(WavesDemoAdaptors, BaseGalaxyJobAdaptor, ):
    def _prepare_job(self, job):
        return WavesDemoAdaptors._prepare_job(self, job)

    def _run_job(self, job):
        return WavesDemoAdaptors._run_job(self, job)

    def _job_status(self, job):
        return WavesDemoAdaptors._job_status(self, job)

    def _job_results(self, job):
        return True

    def _cancel_job(self, job):
        pass

    def _job_run_details(self, job):
        return job.default_run_details()
