from __future__ import unicode_literals

from os.path import join
import random
from waves.adaptors.galaxy.tool import GalaxyJobAdaptor as BaseGalaxyJobAdaptor
from waves.wcore.adaptors.cluster import LocalClusterAdaptor as BaseLocalClusterAdaptor
from waves.wcore.adaptors.cluster import SshClusterAdaptor as BaseSshClusterAdaptor
from waves.wcore.adaptors.cluster import SshKeyClusterAdaptor as BaseSshKeyClusterAdaptor
from waves.wcore.adaptors.mocks import MockJobRunnerAdaptor as BaseMockAdaptor
from waves.wcore.adaptors.shell import LocalShellAdaptor as BaseLocalShellAdaptor
from waves.wcore.adaptors.shell import SshKeyShellAdaptor as BaseSshKeyShellAdaptor
from waves.wcore.adaptors.shell import SshShellAdaptor as BaseSshShellAdaptor


class DemoMockConnector(object):

    def get_job(self, job):
        return job


class WavesDemoAdaptor(BaseMockAdaptor):

    def get_command_line(self, obj):
        """ Retrieve command line normally executed on remote platform """
        if obj.adaptor:
            return "%s %s" % (obj.adaptor.command, obj.command_line)
        else:
            return "Unavailable %s" % obj.command_line

    def _connect(self):
        """ Fake connection when running jobs. """
        self.connector = DemoMockConnector()
        self._connected = True

    def __init__(self, command=None, protocol='http', host="localhost", **kwargs):
        """ Force command and add a job member """
        super(WavesDemoAdaptor, self).__init__(command, protocol, host, **kwargs)
        self.job = None
        self.command = 'mock_command' or command

    def _job_status(self, job):
        """ Mocking job status """
        job.logger.info('Mock job status -- Demo -- ')
        job.job_history.create(message='[Fake job status -- Demo -- ] {}'.format(job.slug), status=job.status)
        return super(WavesDemoAdaptor, self)._job_status(job)

    def _run_job(self, job):
        """ Mocking job launch """
        job.logger.info("Entering fake run -- Demo -- ")
        job.job_history.create(message='[Entering fake run -- Demo -- ] {}'.format(job.slug), status=job.status)
        super(WavesDemoAdaptor, self)._run_job(job)
        return job

    def _prepare_job(self, job):
        """ Mocking job preparation """
        job.logger.info("Entering fake prepare -- Demo -- ")
        job.job_history.create(message='[Entering fake prepare -- Demo -- ] {}'.format(job.slug), status=job.status)
        return job

    def _job_run_details(self, job):
        """ Mocking job run details retrieval """
        return job.default_run_details()

    def _job_results(self, job):
        """ Mocking job results, add basic command line to standard output,
         Randomly set stderr output to see warnings happen
         """
        for output in job.outputs.all():
            if output.value != job.stderr or bool(random.getrandbits(1)):
                with open(join(output.file_path), 'w') as fp:
                    fp.write("Should contain expected content for {} ".format(output.name))

        with open(join(job.working_dir, job.stdout), 'w') as fp:
            fp.write("Executed command on computing infrastructure : {}".format(self.get_command_line(job)))
        return True


class SshShellAdaptor(WavesDemoAdaptor, BaseSshShellAdaptor):
    pass


class LocalClusterAdaptor(WavesDemoAdaptor, BaseLocalClusterAdaptor):
    pass


class SshKeyShellAdaptor(WavesDemoAdaptor, BaseSshKeyShellAdaptor):
    pass


class LocalShellAdaptor(WavesDemoAdaptor, BaseLocalShellAdaptor):
    pass


class SshClusterAdaptor(WavesDemoAdaptor, BaseSshClusterAdaptor):
    pass


class SshKeyClusterAdaptor(WavesDemoAdaptor, BaseSshKeyClusterAdaptor):
    pass


class GalaxyJobAdaptor(BaseGalaxyJobAdaptor, WavesDemoAdaptor):
    def _prepare_job(self, job):
        """ Mocking job remote preparation """
        return WavesDemoAdaptor._prepare_job(self, job)

    def _run_job(self, job):
        return WavesDemoAdaptor._run_job(self, job)

    def _job_status(self, job):
        return WavesDemoAdaptor._job_status(self, job)

    def _job_results(self, job):
        return True

    def _cancel_job(self, job):
        pass

    def _job_run_details(self, job):
        return job.default_run_details()
