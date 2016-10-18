from __future__ import unicode_literals


from django.db import transaction
from waves.models.services import Service, ServiceInputFormat, ServiceSubmission


class Importer(object):
    _update = False
    _service = None
    _formatter = None
    _tool_client = None
    _order_input = 0
    _submission = None

    def __init__(self, adaptor, service=None, runner=None):
        """
        Args:
            runner: A Runner model object (mandatory)
            service: A existing service to update or create when not specified
        """
        import logging
        self.logger = logging.getLogger(__name__)
        self._formatter = ServiceInputFormat()
        self._adaptor = adaptor
        self._runner = runner
        if service is not None:
            # Service update
            self._service = service
            self._runner = service.run_on
            # replace self._adaptor with service configurated one
            self._adaptor = service.adaptor
            self._service.submissions.all().delete()
            self._update = True

    @transaction.atomic()
    def import_remote_service(self, remote_tool_id):
        """
        For specified Adaptor remote tool identifier, try to import submission params
        :param remote_tool_id: Adaptors provider remote tool identifier
        :return: Update service with new submission according to retrieved parameters
        :rtype: :class:`waves.models.services.Service`
        """
        self.connect()
        self._adaptor.remote_tool_id = remote_tool_id

        if not self._service:
            # import is for a new service
            from waves.models.runners import Runner
            self.logger.debug("New Service from adaptor")
            # try to get one runner with parameters
            if self._runner is None:
                self._runner = Runner.objects.create(
                    clazz=self._adaptor.__module__ + '.' + self._adaptor.__class__.__name__,
                    name='Imported runner default')
            self._service = Service.objects.create(name='Imported service', run_on=self._runner,
                                                   api_name='new_imported_service_1.0', version="1.0")
            self._submission = self._service.default_submission
        else:
            self._submission = ServiceSubmission.objects.create(service=self._service, label="Imported submission",
                                                                default=False)
            self._service.submissions.add(self._submission)
        # First update service description / metas if possible
        self._update_service(self._get_tool_details(remote_tool_id))
        # list all services inputs
        remote_inputs = self._list_remote_inputs(remote_tool_id)
        self.logger.debug('Import service %i inputs ', len(remote_inputs))
        self._submission.service_inputs.all().delete()
        service_inputs = self._import_service_inputs(remote_inputs)
        # update related or create new
        # configure the new submission
        self._submission.service_inputs.set(service_inputs, bulk=False, clear=True)
        # list all services outputs
        remote_outputs = self._list_remote_outputs(remote_tool_id)
        # for each output retrieved import_service_output
        self.logger.debug('Import service %i outputs', len(remote_outputs))
        self._service.service_outputs.all().delete()
        service_outputs = self._import_service_outputs(remote_outputs)
        # update related objects
        self._service.service_outputs.set(service_outputs, bulk=False, clear=True)
        # retrieve potential exit codes
        exit_codes = self._list_exit_codes(remote_tool_id)
        self.logger.debug('Import service %i exit codes ', len(exit_codes))
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
        self.connect()
        return self._list_all_remote_services()

    def _list_all_remote_services(self):
        raise NotImplementedError

    def connect(self):
        pass
