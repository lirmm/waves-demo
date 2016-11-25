from __future__ import unicode_literals

import logging

import bioblend
import six
from bioblend.galaxy.client import ConnectionError

import waves.const
import waves.settings
from waves.exceptions import RunnerConnectionError
from waves.importers.galaxy.tool import GalaxyToolImporter
from waves.models import ServiceInput

logger = logging.getLogger(__name__)


class GalaxyWorkFlowImporter(GalaxyToolImporter):
    """
    Galaxy Workflow service importer
    """
    workflow = None
    workflow_full_description = None

    def connect(self):
        """
        Connect to remote Galaxy Host
        :return:
        """
        self._tool_client = bioblend.galaxy.objects.client.ObjWorkflowClient(self._adaptor.connect())

    def _list_all_remote_services(self):
        try:

            tool_list = self._tool_client.list()
            return [
                (y.id, y.name) for y in tool_list if y.published is True
                ]
        except ConnectionError as e:
            raise RunnerConnectionError(e.message, 'Connection Error:\n')

    def _list_remote_inputs(self, tool_id):
        logger.warn('Not Implemented yet')
        wl = self._tool_client.get(id_=tool_id)
        wc = bioblend.galaxy.workflows.WorkflowClient(self._tool_client.gi)
        wc.export_workflow_to_local_path(workflow_id=tool_id,
                                         file_local_path=waves.settings.WAVES_DATA_ROOT + '/' + tool_id + '.json',
                                         use_default_filename=False)
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug('inputs %s', wl.inputs)
            logger.debug('inputs_i %s', wl.data_input_ids)
            logger.debug('inputs %s', wl.inputs['0'])
            logger.debug('labels %s', wl.input_labels)
            logger.debug('runnable %s', wl.is_runnable)
        for id_step in wl.sorted_step_ids():
            step = wl.steps[id_step]
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug('step  %s %s %s:', step.type, ' name ', step.name)
                logger.debug('input_steps %s', step.input_steps)
                logger.debug('tool_inputs %s', step.tool_inputs)
                logger.debug('tool_id %s', step.tool_id)
        return wl.inputs

    def _list_remote_outputs(self, tool_id):
        logger.warn('Not Implemented yet')
        return []

    def _list_exit_codes(self, tool_id):
        logger.warn('Not Implemented yet')
        return []

    def _get_tool_details(self, remote_tool_id):
        self.workflow = self._tool_client.get(id_=remote_tool_id)
        self.workflow_full_description = self.workflow.export()
        # TODO refactor this to import values from workflow
        return waves.const.ImportService(name='new workflow', version='1.0', short_description="",
                                         wrapped=self.workflow.inputs['0'])

    def _update_service(self, details):
        if not self._service.short_description:
            self._service.short_description = details.name
        self._service.name = details.name
        # check whether another service exists with same generated api_name
        self._update_remote_tool_id(details.id)
        self._service.save()

    def _import_service_inputs(self, data):
        service_inputs = []
        for dat in six.iteritems(data):
            dic = dat[-1]
            service_input = ServiceInput(name=dic['label'],
                                         label=dic['label'],
                                         service=self._service,
                                         type=waves.const.TYPE_FILE,
                                         default=dic['value'],
                                         mandatory=True)
            logger.debug('Service input %s ', service_input)
            service_inputs.append(service_input)
        return service_inputs