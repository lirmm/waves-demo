""" WAVES base class for Service Importer """

from __future__ import unicode_literals

import logging

from django.db import transaction
from waves.models import ServiceInputFormat, Service, ServiceSubmission, Runner
import waves.const
logger = logging.getLogger(__name__)


class AdaptorImporter(object):
    """Base AdaptorImporter class, define process which must be implemented in concrete sub-classes """
    _update = False
    _service = None
    _runner = None
    _formatter = None
    _tool_client = None
    _order_input = 0
    _submission = None

    def __init__(self, adaptor):
        """
        Args:
            runner: A Runner model object (mandatory)
            service: A existing service to update or create when not specified
        """
        self._formatter = ServiceInputFormat()
        self._adaptor = adaptor

    @transaction.atomic()
    def import_remote_service(self, remote_tool_id, for_who):
        """
        For specified Adaptor remote tool identifier, try to import submission params
        :param for_who: Which of Service or Runner instance this importer should run for
        :param remote_tool_id: Adaptors provider remote tool identifier
        :return: Update service with new submission according to retrieved parameters
        :rtype: :class:`waves.models.services.Service`
        """
        self.connect()
        tool_details = self._get_tool_details(remote_tool_id)
        if isinstance(for_who, Runner):
            self._runner = for_who
            self._service = Service(name=tool_details.name, run_on=self._runner, version=tool_details.version,
                                    short_description=tool_details.short_description,
                                    remote_service_id=str(remote_tool_id))
            self._service.save()
            self._service._run_on = self._runner
        elif isinstance(for_who, Service):
            # Service update
            self._service = for_who
            self._update_service(tool_details)
            self._service.remote_service_id = str(remote_tool_id)
            self._runner = for_who.run_on
            # replace self._adaptor with service configured one
            self._adaptor = for_who.adaptor
            self._update = True
        self._update_remote_tool_id(remote_tool_id)
        # list all services inputs
        self._submission = ServiceSubmission.objects.create(label='Imported submission', service=self._service,
                                                            available_online=True, available_api=True)
        self._service.submissions.add(self._submission)
        remote_inputs = self._list_remote_inputs(remote_tool_id)
        logger.debug('Import service %i inputs ', len(remote_inputs))
        self._submission.service_inputs.all().delete()
        service_inputs = self._import_service_inputs(remote_inputs)
        # update related or create new
        # configure the new submission
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
        """ Update service version status """
        pass

    def _update_remote_tool_id(self, remote_tool_id):
        """ Some Adaptors store remote_tool_id in their configuration """
        pass

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
        #  'version', 'short_description'
        return waves.const.ImportService('New Service', '1.0', 'Imported new Service default description')

    def set_service(self, service):
        self._service = service
        self._adaptor = service.adaptor

    def list_all_remote_services(self):
        self.connect()
        return self._list_all_remote_services()

    def _list_all_remote_services(self):
        raise NotImplementedError

    def connect(self):
        pass