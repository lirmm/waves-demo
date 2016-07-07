from __future__ import unicode_literals

import logging

from django.db import transaction

from waves.models.services import Service, ServiceInputFormat

logger = logging.getLogger(__name__)


class ToolRunnerImporter(object):
    _update = False
    _service = None
    _formatter = None
    _tool_client = None
    _order_input = 0

    def __init__(self, runner_model, service=None):
        """
        Args:
            runner_model: A Runner model object (mandatory)
            service: A existing service to update or create when not specified
        """
        self._formatter = ServiceInputFormat()

        if service is not None:
            logger.debug("Existing service %s", service)
            self._service = service
            self._runner = service.runner
        else:
            logger.debug("New Service from runner")
            self._service = Service.objects.create(name='New imported service', run_on=runner_model)
            self._runner = runner_model.runner
        self._update = (self._service is None)

    @transaction.atomic()
    def import_remote_service(self, remote_tool_id):
        remote_details = self._get_tool_details(remote_tool_id)
        # First update service description / metas if possible
        self._update_service(remote_details)
        # save service
        # list all services inputs
        remote_inputs = self._list_remote_inputs(remote_tool_id)
        logger.debug('Import service %i inputs ', len(remote_inputs))
        self._service.service_inputs.all().delete()
        service_inputs = self._import_service_inputs(remote_inputs)
        # update related or create new
        self._service.service_inputs.set(service_inputs, bulk=False, clear=True)
        # list all services outputs
        remote_outputs = self._list_remote_outputs(remote_tool_id)
        # for each output retrieved import_service_output
        logger.debug('Import service %i outputs', len(remote_outputs))
        self._service.service_outputs.all().delete()
        service_outputs = self._import_service_outputs(remote_outputs)
        # update related objects
        self._service.service_outputs.set(service_outputs, bulk=False, clear=True)

        # retrieve potential exit codes
        exit_codes = self._list_exit_codes(remote_tool_id)
        logger.debug('Import service %i exit codes ', len(exit_codes))
        self._service.service_exit_codes.all().delete()
        self._service.service_exit_codes.set(exit_codes, bulk=False, clear=True)

    def _update_service(self, details):
        raise NotImplementedError

    def _list_remote_inputs(self, tool_id):
        raise NotImplementedError

    def _list_remote_outputs(self, tool_id):
        raise NotImplementedError

    def _import_service_inputs(self, data):
        raise NotImplementedError

    def _import_service_outputs(self, data):
        raise NotImplementedError

    def _list_exit_codes(self, tool_id):
        raise NotImplementedError

    def _get_tool_details(self, remote_tool_id):
        raise NotImplementedError

    def set_service(self, service):
        assert isinstance(service, Service)
        self._service = service
        self._runner = service.runner

    def list_all_remote_services(self):
        raise NotImplementedError


