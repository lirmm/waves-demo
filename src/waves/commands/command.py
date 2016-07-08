from __future__ import unicode_literals

import logging

from waves.models import Service, JobInput

logger = logging.getLogger(__name__)


class BaseCommand(object):

    def __init__(self, service):
        assert isinstance(service, Service)
        self.service = service

    def create_command_line(self, job_inputs):
        """
        Parse and create command line text to launch service
        Args:
            job_inputs: JobInput objects list

        Returns:
            str the command line text
        """
        return ' '.join(self.get_command_line_element_list(job_inputs))

    def get_command_line_element_list(self, job_inputs):
        return filter(None, [e.command_line_element for e in job_inputs])

