from __future__ import unicode_literals

import logging

from django.db import transaction

from waves.models.services import Service, ServiceInputFormat, ServiceSubmission

logger = logging.getLogger(__name__)


class ToolRunnerImporter(object):
    _update = False
    _service = None
    _formatter = None
    _tool_client = None
    _order_input = 0
    _submission = None

    def __init__(self, runner, service=None):
        """
        Args:
            runner: A Runner model object (mandatory)
            service: A existing service to update or create when not specified
        """
        self._formatter = ServiceInputFormat()
        self._adaptor = runner
        if service is not None:
            logger.debug("Existing service %s", service)
            self._service = service
            self._adaptor = service.adaptor
            self._service.submissions.all().delete()
            self._update = True

    def _init_runner(self):
        self.connect()

    @transaction.atomic()
    def import_remote_service(self, remote_tool_id):
        self._init_runner()
        if not self._service:
            # import is for a new service
            logger.debug("New Service from adaptor")
            self._service = Service.objects.create(name='New imported service', run_on=self._runner,
                                                   api_name='new_imported_service', version="1.0")
        self._submission = ServiceSubmission.objects.create(service=self._service)
        self._service.submissions.add(self._submission)

        remote_details = self._get_tool_details(remote_tool_id)
        # First update service description / metas if possible
        self._update_service(remote_details)
        # save service
        # list all services inputs
        remote_inputs = self._list_remote_inputs(remote_tool_id)
        logger.debug('Import service %i inputs ', len(remote_inputs))
        self._submission.service_inputs.all().delete()
        service_inputs = self._import_service_inputs(remote_inputs)
        # update related or create new
        # create a new submission
        self._submission.service_inputs.set(service_inputs, bulk=False, clear=True)
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
        return self._service

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
        self._service = service
        self._adaptor = service.adaptor

    def list_all_remote_services(self):
        self._init_runner()
        return self._list_all_remote_services()

    def _list_all_remote_services(self):
        raise NotImplementedError

    def connect(self):
        pass

