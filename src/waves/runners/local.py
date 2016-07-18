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

    def __init__(self, **kwargs):
        super(ShellJobRunner, self).__init__(**kwargs)

    @property
    def init_params(self):
        return dict(command=self.command)

    def _connect(self):
        self._connected = True

    def _disconnect(self):
        self._connector = None
        self._connected = False

    def _prepare_job(self, job):
        """
        - Create a new history from job data (hashkey as identifier)
        - upload job input files to galaxy in this newly created history
            - associate uploaded files galaxy id with input
        Raises:
            RunnerNotInitialized
        Args:
            job: the job to prepare

        Returns:
            None
        """
        pass

    def _run_job(self, job):
        """
        Launch the job with current parameters from associated history
        Args:
            job:
        """
        pass

    def _cancel_job(self, job):
        """Jobs cannot be cancelled for Galaxy runners
        """
        pass

    def _job_status(self, job):
        pass

    def _job_results(self, job):
        pass

    def _job_run_details(self, job):
        pass
