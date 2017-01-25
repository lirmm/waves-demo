""" WAVES base class for Service Importer """

from __future__ import unicode_literals

import logging
import os
import waves.adaptors
import waves.adaptors.const
from waves.models import BaseParam, Service

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
    _exit_codes = None
    #: Some fields on remote connectors need a mapping for type between standard WAVES and theirs
    _type_map = {}
    _warnings = []
    _errors = []

    def __init__(self, adaptor):
        """
        Initialize a Import from it's source adaptor
        :param adaptor: a BaseAdaptor object, providing connection support
        """
        self._formatter = InputFormat()
        self._adaptor = adaptor
        logger.info('=' * 14 + '=' * len(str(adaptor)))
        logger.info('Importer Init %s', adaptor)
        logger.info('=' * 14 + '=' * len(str(adaptor)))

    def __str__(self):
        return self.__class__.__name__

    @property
    def connected(self):
        return self._adaptor.connected

    def import_service(self, tool_id):
        """
        For specified Adaptor remote tool identifier, try to import submission params
        :param tool_id: Adaptors provider remote tool identifier
        :return: Update service with new submission according to retrieved parameters
        :rtype: :class:`waves.models.services.Service`
        """
        self.connect()
        self._warnings = []
        self._errors = []
        service_details, inputs, outputs, exit_codes = self.load_tool_details(tool_id)
        if service_details:
            logger.debug('Import Service %s', tool_id)
            self._service = service_details
            logger.debug('Service %s', service_details.name)
            self._service.inputs = self.import_service_params(inputs)
            self._service.outputs = self.import_service_outputs(outputs)
            self._service.exit_codes = self.import_exit_codes(exit_codes)
        else:
            logger.warn('No service retrieved (%s)', tool_id)
            return None
        # TODO manage exit codes
        if logger.isEnabledFor(logging.INFO):
            logger.info('------------------------------------')
            logger.info(self._service.info())
            logger.info('------------------------------------')
            if self.warnings or self.errors:
                logger.warn('*** // WARNINGS // ***')
                for warn in self.warnings:
                    logger.warn('=> %s', warn.message)
            if self.errors:
                logger.warn('*** // ERRORS // ***')
                for error in self.errors:
                    logger.error('=> %s', error.message)
            logger.info('------------')
            logger.info('-- Inputs --')
            logger.info('------------')
            for service_input in self._service.inputs:
                logger.info(service_input.info())
            logger.info('-------------')
            logger.info('-- Outputs --')
            logger.info('-------------')
            for service_output in self._service.outputs:
                logger.info(service_output.info())
            logger.info('------------------------------------')
        return self._service

    def list_services(self):
        """ Get and return a list of tuple ('Category, ['Service Objects' list])  """
        if not self.connected:
            self.connect()
        return self._list_services()

    def connect(self):
        return self._adaptor.connect()

    @property
    def warnings(self):
        return self._warnings

    def warn(self, base_warn):
        self._warnings.append(base_warn)

    @property
    def errors(self):
        return self._errors

    def error(self, base_error):
        if base_error is None:
            return self._errors
        self._errors.append(base_error)

    def import_service_params(self, data):
        raise NotImplementedError()

    def import_service_outputs(self, data):
        raise NotImplementedError()

    def import_exit_codes(self, tool_id):
        raise NotImplementedError()

    def load_tool_details(self, tool_id):
        """ Return a Service Object instance with added information if possible """
        return NotImplementedError()

    def _list_services(self):
        raise NotImplementedError()

    def map_type(self, type_value):
        """ Map remote adaptor types to JobInput/JobOutput WAVES TYPE"""
        return self._type_map.get(type_value, BaseParam.TYPE_TEXT)


class InputFormat(object):
    """
    ServiceInput format validation
    """

    @staticmethod
    def format_number(number):
        return number

    @staticmethod
    def format_boolean(truevalue, falsevalue):
        return '{}|{}'.format(truevalue, falsevalue)

    @staticmethod
    def format_interval(minimum, maximum):
        return '{}|{}'.format(minimum, maximum)

    @staticmethod
    def format_list(values):
        return os.linesep.join([x.strip(' ') for x in values])

    @staticmethod
    def choice_list(value):
        list_choice = []
        if value:
            try:
                for param in value.splitlines(False):
                    if '|' in param:
                        val = param.split('|')
                        list_choice.append((val[1], val[0]))
                    else:
                        list_choice.append((param, param))
            except ValueError as e:
                logger.warn('Error Parsing list values %s - value:%s - param:%s', e.message, value, param)
        return list_choice