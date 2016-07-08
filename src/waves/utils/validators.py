from __future__ import unicode_literals

import sys
import os
import logging
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)
"""
Dynamic inputs fields validation for job creation
TYPE_BOOLEAN = 'boolean'
TYPE_FILE = 'file'
TYPE_LIST = 'select'
TYPE_INTEGER = 'int'
TYPE_FLOAT = 'float'
TYPE_TEXT = 'text'
"""


# TODO Refactoring this in a concrete class with validation more explicit error messages
class ServiceInputValidator(object):

    message = '%s is not valid %s (%s) got: %s'
    extra_message = ''

    def validate_input(self, the_input, value):
        assert the_input is not None
        try:
            validator = '_validate_input_' + the_input.type
            func = getattr(self, validator)
            if not func(the_input, value):
                logger.info('Failed input -%s-, service -%s-, with value %s', the_input, the_input.service, value)
                raise ValidationError(self.message % (the_input.label, the_input.type, self.extra_message, value))
        except AttributeError as e:
            logger.error('Validation error:%s', e.message)
            raise ValidationError('Unknown type for input: %s - type: %s' % (the_input, the_input.type))

    def _validate_input_boolean(self, the_input, value):
        # Add check format values
        self.extra_message = ' allowed values are "yes", "true", "1", "no", "false", "0", "None"'
        return str(value).lower() in ("yes", "true", "1", 'no', 'false', '0', 'none')

    def _validate_input_file(self, the_input, value):
        from django.core.files.base import File
        assert isinstance(value, File)
        # TODO Check file consistency with BioPython ?
        # TODO modify message for more 'user friendly' display
        self.extra_message = 'allowed extension are %s' % str([e[1] for e in the_input.get_choices()])
        _, extension = os.path.splitext(value.name)
        return any(e[1] == extension for e in the_input.get_choices())

    def _validate_input_int(self, the_input, value):
        try:
            int(value)
            if getattr(self, the_input, 'format', False):
                # check min max ?
                pass
            return True
        except ValueError:
            return False

    def _validate_input_float(self, the_input, value):
        try:
            float(value)
            if getattr(self, the_input, 'format', False):
                # check min max ?
                pass
            return True
        except ValueError:
            return False

    def _validate_input_select(self, the_input, value):
        self.extra_message = 'allowed values are %s' % str([e[1] for e in the_input.get_choices()])
        return any(e[0] == value for e in the_input.get_choices())

    def _validate_input_text(self, the_input, value):
        return True
