"""
Author : Marc Chakiachvili
Email: marc.chakiachvili@lirmm.fr
Date : 2015, November
"""
from __future__ import unicode_literals
from django.conf import settings

from waves.runners.runner import JobRunner


class ShellJobRunner(JobRunner):

    command = None
    working_dir = '/tmp'
    base_dir = '/usr/bin'

    def __init__(self, **kwargs):
        super(ShellJobRunner, self).__init__(**kwargs)

    @property
    def init_params(self):
        return dict(command=self.command,
                    working_dir=self.working_dir,
                    base_dir=self.base_dir)

    def _run_job(self, job):
        super(ShellJobRunner, self).run_job(job)

    def _job_results(self, job):
        super(ShellJobRunner, self).job_results(job)

    def _connect(self):
        super(ShellJobRunner, self).connect()

    def _job_status(self):
        return self.commandStatus

    def _get_inputs(self, job):
        # TODO retrieve job input params
        pass

    def _prepare_job(self, job):
        """
        Prepare and setup up command parameters
        :param job: the job object to prepare
        :return: boolean
        """
        self.commandLine = self.command + ' '
        for param in job.atgcjobinput_set.all():
            self.commandLine += param.name + ' = ' if param.name else ''
            self.commandLine += param.value + ' '


    def _cancel_job(self, job):
        raise Exception(u'A local command cannot be cancelled once launched')

    def _disconnect(self, job):
        self._connected = False
        return self._connected

        # def connect(self, job):
        #    self._connected = True
        #    return self._connected

    def _ready(self):
        # TODO check shell availability ?
        return True
