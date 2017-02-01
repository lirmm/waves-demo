""" Galaxy remote platform Services / Workflow Import classes"""
from __future__ import unicode_literals

import logging
import os
import tempfile

import bioblend
import six
from bioblend import ConnectionError
from django.conf import settings

import waves.adaptors.const
from waves.adaptors.core.api.galaxy import GalaxyAdaptorConnectionError
from waves.importers.exceptions import *
from waves.models import Service, BaseParam, SubmissionOutput, RepeatedGroup
from .base import AdaptorImporter

logger = logging.getLogger(__name__)


def _get_input_value(tool_input, field, default=''):
    return tool_input[field] if field in tool_input and tool_input[field] != '' else default


class GalaxyToolImporter(AdaptorImporter):
    """ Allow Service to automatically import submission parameters from Galaxy bioblend API """
    #: List of tools categories which are not meaning a 'WAVES' service tool
    _unwanted_categories = [None, 'Get Data', 'Filter and sort', 'Collection Operations', 'Graph/Display Data',
                            'Send Data', 'Text Manipulation', 'Fetch Alignments', ]

    _type_map = dict(
        text=BaseParam.TYPE_TEXT,
        boolean=BaseParam.TYPE_BOOLEAN,
        integer=BaseParam.TYPE_INTEGER,
        float=BaseParam.TYPE_FLOAT,
        data=BaseParam.TYPE_FILE,
        select=BaseParam.TYPE_LIST,
        conditional=BaseParam.TYPE_LIST,
        data_collection=BaseParam.TYPE_FILE,
        genomebuild=BaseParam.TYPE_LIST,
    )

    def connect(self):
        """
        Connect to remote Galaxy Host
        :return:
        """
        self._adaptor.connect()
        self._tool_client = self._adaptor.connector.tools

    def load_tool_details(self, tool_id):
        try:
            details = self._tool_client.get(id_=tool_id, io_details=True, link_details=True)
            if settings.DEBUG:
                import json
                from waves.adaptors.utils import slugify
                with open(os.path.join(settings.WAVES_TRACE_GALAXY,
                                       slugify(details.id + '_' + details.version) + '.json'),
                          'w') as fp:
                    fp.write(json.dumps(details.wrapped))
            description = details.wrapped.get('description')

            service = Service.objects.create(name=details.name,
                                             description=description,
                                             short_description=description,
                                             edam_topics=','.join(details.wrapped.get('edam_topics')),
                                             edam_operations=','.join(details.wrapped.get('edam_operations')),
                                             remote_service_id=tool_id,
                                             version=details.version)

            return service, details.wrapped.get('inputs'), details.wrapped.get('outputs'), []
        except ConnectionError as e:
            self.error(GalaxyAdaptorConnectionError(e))
            return None, None, None, None

    def _list_services(self):
        """
        List available tools on remote Galaxy server, filtering with ``_unwanted_categories``
        Group items by categories

        :return: A list of tuples corresponding to format used in Django for Choices
        """
        try:
            tool_list = self._tool_client.list()
            group_list = sorted(set(map(lambda x: x.wrapped['panel_section_name'], tool_list)), key=lambda z: z)
            group_list = [x for x in group_list if x not in self._unwanted_categories]
            service_list = [(x,
                             sorted(
                                 (Service(remote_service_id=y.id, name=y.name, version=y.version) for y in tool_list if
                                  y.wrapped['panel_section_name'] == x and y.wrapped['model_class'] == 'Tool'),
                                 key=lambda d: d.name)
                             ) for x in group_list]
            return service_list
        except ConnectionError as e:
            raise GalaxyAdaptorConnectionError(e)

    def import_exit_codes(self, tool_id):
        # TODO see if galaxy tool give this info
        return []

    def import_service_params(self, data):
        inputs = []
        logger.debug("Importing %i inputs ", len(data))
        for cur_input in data:
            logger.debug("Current Input %s: %s", cur_input.get('name'), cur_input.get('type'))
            tool_input_type = cur_input.get('type')
            logger.debug("Input type %s mapped to %s", tool_input_type, self.map_type(tool_input_type))
            service_input = None
            if tool_input_type == 'conditional':
                service_input = self._import_conditional_set(cur_input)
            elif tool_input_type == 'section':
                service_input = self.import_service_params([sect_input for sect_input in cur_input.get('inputs')])
            elif tool_input_type == 'repeat':
                repeat_group = self._import_repeat(cur_input)
                # print "repeat Group ", repeat_group
                service_input = self.import_service_params([rep_input for rep_input in cur_input.get('inputs')])
                for srv_input in service_input:
                    # print "srv_input", srv_input
                    srv_input.repeat_group = repeat_group
            elif tool_input_type == 'expand':
                self.warn(UnmanagedInputTypeException("Expand"))
            else:
                service_input = self._import_param(cur_input)
            if service_input is not None:
                if type(service_input) is list:
                    inputs.extend(service_input)
                else:
                    inputs.append(service_input)
        return inputs

    def _import_param(self, tool_input):
        try:
            if tool_input.get('is_dynamic', False):
                raise UnmanagedInputTypeException(
                    'Dynamic field \'%s\':%s ' % (tool_input.get('name'), tool_input.get('label')))
            # TODO manage subclasses
            srv_input = BaseParam(label=tool_input.get('label', tool_input.get('name', None)),
                                  name=tool_input.get('name'),
                                  default=tool_input.get('default', None),
                                  help_text=tool_input.get('help'),
                                  type=self.map_type(tool_input.get('type')),
                                  mandatory=tool_input.get('optional', False),
                                  )
            _import_func = getattr(self, '_import_' + tool_input.get('type', 'text'))
            logger.debug('import func _import_%s ', _import_func.__name__)
            _import_func(tool_input, srv_input)
            if 'edam' in tool_input:
                if 'edam_formats' in tool_input['edam']:
                    srv_input.edam_formats = ','.join(tool_input['edam']['edam_formats'])
                    srv_input.edam_datas = ','.join(tool_input['edam']['edam_data'])
            return srv_input
        except UnmanagedInputTypeException as e:
            self.warn(e)
            return None
        except KeyError:
            self.warn(
                UnManagedAttributeTypeException(
                    "%s:%s" % (tool_input['type'], tool_input['name'])))
            return None
        except AttributeError:
            self.warn(
                UnManagedAttributeException("%s:%s:%s" % (tool_input['type'], tool_input['name'], tool_input['label'])))
            return None
        except Exception as e:
            self.error(Exception('UnexpectedError for input "%s" (%s)' % (tool_input['name'], e)))
            return None

    def _import_conditional_set(self, tool_input):
        conditional = self._import_param(tool_input.get('test_param'))
        logger.debug('Test param %s', tool_input['test_param'])
        for related in tool_input.get('cases', []):
            when_value = related.get('value')
            for when_input in related['inputs']:
                # TODO manage subclasses
                when_service_input = BaseParam(label=when_input.get('label', when_input.get('name')),
                                               name=when_input.get('name'),
                                               default=when_input.get('value'),
                                               description=when_input.get('help'),
                                               short_description=when_input.get('help'),
                                               type=self.map_type(when_input.get('type')),
                                               mandatory=False,
                                               when_value=when_value)
                when_input_type = when_input.get('type')
                try:
                    if when_input_type == 'conditional':
                        self.error(
                            UnmanagedInputTypeException(
                                "Unmanaged nested conditional inputs %s " % when_input.get('name')))
                        raise RuntimeWarning

                    _import_func = getattr(self, '_import_' + when_input.get('type', 'text'))
                    logger.debug('import func _import_%s ', _import_func.__name__)
                    _import_func(when_input, when_service_input)
                except AttributeError as e:
                    self.error(Exception('UnexpectedError for input "%s" (%s)' % (when_input.get('name'), e)))
                except RuntimeWarning:
                    pass
                else:
                    conditional.dependents.append(when_service_input)
        return conditional

    def _import_text(self, tool_input, service_input):
        # TODO check if format needed
        pass

    def _import_boolean(self, tool_input, service_input):
        truevalue = tool_input.get('truevalue', True)
        falsevalue = tool_input.get('falsevalue', False)
        service_input.format = self._formatter.format_boolean(truevalue, falsevalue)

    def _import_integer(self, tool_input, service_input):
        return self._import_number(tool_input, service_input)

    def _import_float(self, tool_input, service_input):
        return self._import_number(tool_input, service_input)

    def _import_number(self, tool_input, service_input):
        service_input.default = tool_input.get('value')
        if 'min' in tool_input:
            _min = tool_input.get('min', '')
        if 'max' in tool_input:
            _max = tool_input.get('max', '')
        service_input.format = self._formatter.format_interval(_min, _max)

    def _import_data(self, tool_input, service_input):
        service_input.format = self._formatter.format_list(_get_input_value(tool_input, 'extensions'))
        service_input.multiple = _get_input_value(tool_input, 'multiple') is True

    def _import_select(self, tool_input, service_input):
        service_input.default = _get_input_value(tool_input, 'value')
        options = []
        for option in _get_input_value(tool_input, 'options'):
            if option[1] == '':
                option[1] = 'None'
            options.append('|'.join([option[0], option[1]]))
        service_input.format = self._formatter.format_list(options)

    def _import_repeat(self, tool_input, service_input=None):
        return RepeatedGroup.objects.create(name=_get_input_value(tool_input, 'name'),
                                            title=_get_input_value(tool_input, 'title'),
                                            max_repeat=_get_input_value(tool_input, 'max'),
                                            min_repeat=_get_input_value(tool_input, 'min'),
                                            default=_get_input_value(tool_input, 'default'))

    def _import_genomebuild(self, tool_input, service_input):
        return self._import_select(tool_input, service_input)

    def import_service_outputs(self, outputs):
        logger.debug(u'Managing service outputs')
        service_outputs = []
        index = 0
        for tool_output in outputs:
            logger.debug(tool_output.keys())
            service_output = SubmissionOutput.objects.create(name=tool_output.get('name'),
                                                             label=tool_output.get('label'),
                                                             ext=tool_output.get('format'),
                                                             edam_format=tool_output.get('edam_format'),
                                                             edam_data=tool_output.get('edam_data'),
                                                             help_text=tool_output.get('label'))

            service_output.order = index
            if service_output.pattern.startswith('$'):
                pass
                # TODO repair relationship between inputs
                # input_related_name = service_output.description[2:-1]
                # service_output.from_input = True
                # related_input = Input.objects.get(name=input_related_name)
                # submission_related_output = RelatedInput(srv_input=related_input)
                # service_output.from_input_submission.add(submission_related_output, bulk=True)
                # service_output.description = "Issued from input '%s'" % input_related_name
            service_outputs.append(service_output)
            index += 1
        return service_outputs

    def _import_section(self, section):
        return self.import_service_params(section['inputs'])


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

    def _list_services(self):
        try:

            tool_list = self._tool_client.list()
            return [
                (y.id, y.name) for y in tool_list if y.published is True
                ]
        except ConnectionError as e:
            raise GalaxyAdaptorConnectionError(e)

    def _list_remote_inputs(self, tool_id):
        logger.warn('Not Implemented yet')
        wl = self._tool_client.get(id_=tool_id)
        wc = bioblend.galaxy.workflows.WorkflowClient(self._tool_client.gi)
        with tempfile.TemporaryFile() as tmp_file:
            wc.export_workflow_to_local_path(workflow_id=tool_id,
                                             file_local_path=os.path.join(tempfile.gettempdir(), tmp_file.name),
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

    def import_exit_codes(self, tool_id):
        logger.warn('Not Implemented yet')
        return []

    def load_tool_details(self, tool_id):
        self.workflow = self._tool_client.get(id_=tool_id)
        self.workflow_full_description = self.workflow.export()
        # TODO refactor this to import values from workflow
        return waves.const.ImportService(name='new workflow', version='1.0', short_description="",
                                         wrapped=self.workflow.inputs['0'])

    def import_service_params(self, data):
        service_inputs = []
        for dat in six.iteritems(data):
            dic = dat[-1]
            service_input = BaseParam.objects.create(name=dic['label'],
                                                     label=dic['label'],
                                                     submission=self._service,
                                                     default=dic['value'],
                                                     mandatory=True)
            logger.debug('Service input %s ', service_input)
            service_inputs.append(service_input)
        return service_inputs
