from __future__ import unicode_literals

import logging
import bioblend
import six
import json
from bioblend.galaxy.client import ConnectionError
from bioblend.galaxy.objects import galaxy_instance as galaxy
from django.conf import settings

import waves.const
from waves.runners.importer import ToolRunnerImporter
from waves.models.services import ServiceInputFormat
from waves.models import RelatedInput, ServiceOutput, ServiceInput, Service

logger = logging.getLogger(__name__)


class GalaxyToolImporter(ToolRunnerImporter):
    def __init__(self, runner_model, service=None):
        super(GalaxyToolImporter, self).__init__(runner_model, service)
        self._tool_client = bioblend.galaxy.objects.client.ObjToolClient(self._runner.connect())

    def list_all_remote_services(self):
        tool_list = self._tool_client.list()
        tool_list.sort(key=lambda tool: tool.name, reverse=False)
        return [(g.id, g.name) for g in tool_list]

    def _update_remote_tool_id(self, remote_tool_id):
        param_service = self._service.runner_params.get(name='remote_tool_id');
        self._service.service_run_params.update_or_create(param__name='remote_tool_id',
                                                          defaults={'value': remote_tool_id,
                                                                    'service': self._service,
                                                                    'param': param_service}, )
        logger.debug('runner_params %s ',
                     self._service.service_run_params.values_list('value', 'param__name', 'param__default'))

    def _update_service(self, details):
        self._service.short_description = self._get_input_value(details.wrapped, 'description',
                                                                self._service.short_description)
        self._service.name = details.name
        self._service.version = details.version
        self._service.set_api_name()
        # check whether another service exists with same generated api_name
        existing_service = Service.objects.filter(api_name__startswith=self._service.api_name)
        if existing_service.count() > 0:
            self._service.api_name += '_%i' % existing_service.count()
            logger.debug('Setting api_name to %s', self._service.api_name)
        self._update_remote_tool_id(details.id)
        self._service.save()

    def _list_remote_inputs(self, tool_id):
        tool_details = self._get_tool_details(tool_id)
        return tool_details.wrapped['inputs']

    def _list_remote_outputs(self, tool_id):
        tool_details = self._get_tool_details(tool_id)
        return tool_details.wrapped['outputs']

    def _list_exit_codes(self, tool_id):
        # TODO see if galaxy tool give this info
        return []

    def _get_tool_details(self, remote_tool_id):
        return self._tool_client.get(id_=remote_tool_id, io_details=True, link_details=True)

    @staticmethod
    def _get_input_value(tool_input, field, default=''):
        return tool_input[field] if field in tool_input and tool_input[field] != '' else default

    def _import_service_inputs(self, data):
        service_inputs = []
        for tool_input in data:
            if 'test_param' in tool_input:
                service_inputs.extend(self._import_conditional_set(tool_input))
            elif 'inputs' in tool_input:
                # section is just rendered as included inputs tag
                service_inputs.extend(self._import_section(tool_input))
            elif 'repeat' in tool_input:
                service_input = ServiceInput(name=tool_input['name'],
                                             label=self._get_input_value(tool_input, 'label', tool_input['name']),
                                             service=self._service,
                                             multiple=True,
                                             default=self._get_input_value(tool_input, 'value', ''))
                service_input = self._import_param(tool_input, service_input)
                if service_input is not None:
                    service_input.save()
                    service_inputs.append(service_input)
            elif 'expand' not in tool_input:
                service_input = ServiceInput(name=tool_input['name'],
                                             label=self._get_input_value(tool_input, 'label', tool_input['name']),
                                             service=self._service,
                                             default=self._get_input_value(tool_input, 'value', ''))
                service_input = self._import_param(tool_input, service_input)
                if service_input is not None:
                    service_input.save()
                    service_inputs.append(service_input)
                    # service_inputs.extend(self._import_conditional_input(tool_input['test_param']))
        if logger.isEnabledFor(logging.DEBUG):
            for service_input in service_inputs:
                logger.debug('****' + service_input.label + ' - ' + service_input.name + '****')
                logger.debug('__class__ ' + str(service_input.__class__))
                logger.debug('Type ' + str(service_input.type) + '|' + service_input.get_type_display())
                logger.debug('Mandatory ' + str(service_input.mandatory))
                logger.debug('Help ' + str(service_input.description))
                logger.debug('Default ' + str(service_input.default))
                if isinstance(service_input, RelatedInput):
                    logger.debug('Depends on ' + str(service_input.related_to))
                    logger.debug('Value ' + service_input.when_value)
                logger.debug('Format ' + str(service_input.format))
                # raise ValueError('A value error is set !!!')
        return service_inputs

    def _import_param(self, tool_input, service_input):
        try:
            logger.debug('---------------')
            service_input.type = self._runner.map_type(tool_input['type'])
            logger.debug('name ' + tool_input['name'])
            service_input.mandatory = self._get_input_value(tool_input, 'optional', 'True') is False
            logger.debug('mandatory ' + str(service_input.mandatory))
            service_input.description = self._get_input_value(tool_input, 'help')
            logger.debug('description ' + str(service_input.description))
            result = getattr(self, '_import_' + tool_input['type'])
            logger.debug('import func _import_%s ', tool_input['type'])
            result(tool_input, service_input)
            logger.debug('result %s ', tool_input['type'])
            logger.debug("default : %s ", service_input.default)
            service_input.param_type = ServiceInputFormat.param_type_from_value(service_input.default)
            service_input.order = self._order_input
            self._order_input += 1
            if service_input.param_type is None:
                service_input.param_type = waves.const.OPT_TYPE_POSIX
            logger.debug("param_type: %s ", service_input.param_type)
            return service_input
        except KeyError as e:
            logger.warn(u'Unmanaged input param type "' + tool_input['type'] + u'" for input "' + tool_input['name'] +
                        u'"\n' + e.message)
            return None
        except Exception as exc:
            logger.warn(u'Unexpected error "%s" for input "%s"', tool_input['type'], tool_input['name'])
            raise exc
        finally:
            logger.debug('---------------')

    def _import_conditional_set(self, tool_input):
        if 'cases' in tool_input:
            conditional_inputs = []
            conditional = ServiceInput(name=tool_input['name'],
                                       label=self._get_input_value(tool_input['test_param'], 'label',
                                                                   tool_input['name']),
                                       type=waves.const.TYPE_LIST,
                                       service=self._service)
            conditional = self._import_param(tool_input['test_param'], conditional)
            conditional.save()
            conditional_inputs.append(conditional)

            for tool_input in tool_input['cases']:
                when_value = tool_input['value']
                for when_input in tool_input['inputs']:
                    when_service_input = RelatedInput(name=when_input['name'],
                                                      label=self._get_input_value(when_input, 'label',
                                                                                  when_input['name']),
                                                      service=self._service,
                                                      related_to=conditional,
                                                      mandatory=False,
                                                      when_value=when_value)
                    when_service_input = self._import_param(when_input, when_service_input)
                    when_service_input.mandatory = False
                    when_service_input.when_value = when_value
                    when_service_input.save()
                    conditional_inputs.append(when_service_input)
            return conditional_inputs

    def _import_text(self, tool_input, service_input):
        # TODO check if format needed
        pass

    def _import_boolean(self, tool_input, service_input):
        truevalue = self._get_input_value(tool_input, 'truevalue')
        falsevalue = self._get_input_value(tool_input, 'falsevalue')
        service_input.format = self._formatter.format_boolean(truevalue, falsevalue)

    def _import_integer(self, tool_input, service_input):
        return self._import_number(tool_input, service_input)

    def _import_float(self, tool_input, service_input):

        return self._import_number(tool_input, service_input)

    def _import_number(self, tool_input, service_input):
        service_input.default = self._get_input_value(tool_input, 'value')
        if 'min' in tool_input:
            _min = self._get_input_value(tool_input, 'min', '')
        if 'max' in tool_input:
            _max = self._get_input_value(tool_input, 'max', '')
        service_input.format = self._formatter.format_interval(_min, _max)

    def _import_data(self, tool_input, service_input):
        service_input.format = self._formatter.format_list(self._get_input_value(tool_input, 'extensions'))
        service_input.multiple = self._get_input_value(tool_input, 'multiple') is True

    def _import_select(self, tool_input, service_input):
        service_input.default = self._get_input_value(tool_input, 'value')
        options = []
        for option in self._get_input_value(tool_input, 'options'):
            if option[1] == '':
                option[1] = 'None'
            options.append('|'.join([option[0], option[1]]))
        service_input.format = self._formatter.format_list(options)

    def _import_service_outputs(self, outputs):
        logger.debug(u'Managing service outputs')
        service_outputs = []
        index = 0
        for tool_output in outputs:
            logger.debug(tool_output.keys())
            service_output = ServiceOutput(name=tool_output['name'])
            service_output.order = index
            service_output.description = self._get_input_value(tool_input=tool_output,
                                                               field='label',
                                                               default=tool_output['name'])
            if service_output.description.startswith('$'):
                from django.core.exceptions import ObjectDoesNotExist
                try:
                    input_related_name = service_output.description[2:-1]
                    service_output.from_input = ServiceInput.objects.get(name=input_related_name,
                                                                         service=self._service)
                    service_output.description = "Issued from input '%s'" % input_related_name
                except ObjectDoesNotExist:
                    logger.warn('Did not found related input by name ' + service_output.description)
            service_output.service = self._service
            service_output.save()
            service_outputs.append(service_output)
            index += 1
        return service_outputs

    def _import_section(self, tool_input):
        return self._import_service_inputs(tool_input['inputs'])


class GalaxyWorkFlowImporter(GalaxyToolImporter):
    def __init__(self, runner_model, service=None):
        super(GalaxyWorkFlowImporter, self).__init__(runner_model, service)
        self._tool_client = bioblend.galaxy.objects.client.ObjWorkflowClient(self._runner.connect())
        self.workflow = None
        self.workflow_full_description = None

    def _list_remote_inputs(self, tool_id):
        logger.warn('Not Implemented yet')
        wl = self._tool_client.get(id_=tool_id)
        wc = bioblend.galaxy.workflows.WorkflowClient(self._tool_client.gi)
        wc.export_workflow_to_local_path(workflow_id=tool_id,
                                         file_local_path=settings.WAVES_DATA_ROOT + '/' + tool_id + '.json',
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
        print self.workflow.inputs
        print self.workflow.steps

        print self.workflow_full_description.__class__, self.workflow_full_description
        return self.workflow

    def _update_service(self, details):
        if not self._service.short_description:
            self._service.short_description = details.name
        self._service.name = details.name
        self._service.set_api_name()
        # check whether another service exists with same generated api_name
        existing_service = Service.objects.filter(api_name__startswith=self._service.api_name)
        if existing_service.count() > 0:
            logger.debug('Setting api_name to %s_%i', self._service.api_name, existing_service.count())
            self._service.api_name += '_%i' % existing_service.count()
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
