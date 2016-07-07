from __future__ import unicode_literals

import logging

from waves.models import Service, JobInput

logger = logging.getLogger(__name__)


class BaseCommand(object):

    def __init__(self, service):
        assert isinstance(service, Service)
        self.service = service

    def create_command_line(self, job_inputs):
        command_line = ""
        for cmd_elem in job_inputs.all():
            assert isinstance(cmd_elem, JobInput)
            logger.debug('Current Command elem %s %s', cmd_elem, cmd_elem.command_line)
            command_line += ' %s' % cmd_elem.command_line
        logger.debug("Command line for srv %s : %s", self.service, command_line)
        return command_line

