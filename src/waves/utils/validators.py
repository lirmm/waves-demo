from __future__ import unicode_literals

import os
import logging

import waves.const

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


# TODO check to go with https://docs.djangoproject.com/en/1.9/ref/validators/
# https://docs.djangoproject.com/en/1.9/ref/forms/validation/


class ServiceInputValidator(object):
    """
    Dynamic validation class for ServiceInput objects, according to ServiceInput type and format
    """
    invalid_message = '%s is not valid %s (%s) got: %s'
    specific_message = ''

    def validate_input(self, the_input, value, form):
        try:
            validator = '_validate_input_' + the_input.type
            func = getattr(self, validator)
            if type(value) == list:
                valid = True
                for val in value:
                    valid = valid and func(the_input, val)
            else:
                valid = func(the_input, value)
            if not valid:
                logger.info('Failed input -%s-, service -%s-, with value %s', the_input, the_input.service, value)
                form.add_error(the_input.name,
                               self.invalid_message % (the_input.label, the_input.type, self.specific_message, value))
            return True
        except AssertionError as e:
            logger.error('Validation error:%s', e.message)
            form.add_error(the_input.name, 'Wrong input "%s": %s' % (the_input, e.message))
        except AttributeError as e:
            logger.error('Validation error:%s', e.message)
            form.add_error(the_input.name, 'Unknown type for input: %s - type: %s' % (the_input, the_input.type))

    def _validate_input_boolean(self, the_input, value):
        # Add check format values
        self.specific_message = ' allowed values are "yes", "true", "1", "no", "false", "0", "None"'
        return str(value).lower() in ("yes", "true", "1", 'no', 'false', '0', 'none') and type(
            value) == bool and the_input.type == waves.const.TYPE_BOOLEAN

    def _validate_input_file(self, the_input, value):
        from django.core.files.base import File
        assert the_input.type == waves.const.TYPE_FILE
        self.specific_message = 'allowed extension are %s' % str([e[1] for e in the_input.get_choices()])
        # TODO Check file consistency with BioPython ?
        # TODO modify message for more 'user friendly' display
        if type(value) == list:
            assert all(isinstance(_, File) for _ in value), '%s is not a valid File' % value
            result = True
            for up_file in value:
                _, extension = os.path.splitext(up_file.name)
                result = result and (any(e[1] == extension for e in the_input.get_choices()))
                return result
        else:
            assert isinstance(value, File), '%s is not a valid File' % value
            _, extension = os.path.splitext(value.name)
            return any(e[1] == extension for e in the_input.get_choices())

    def _validate_input_int(self, the_input, value):
        assert the_input.type == waves.const.TYPE_INTEGER
        self.specific_message = 'value %s is not a valid integer' % value
        try:
            int(value)
            if the_input.format:
                # TODO check min max
                pass
            return True
        except ValueError:
            return False

    def _validate_input_number(self, the_input, value):
        return self._validate_input_int(the_input, value)

    def _validate_input_float(self, the_input, value):
        assert the_input.type == waves.const.TYPE_FLOAT
        self.specific_message = 'value %s is not a valid float' % value
        try:
            float(value)
            if the_input.format:
                # TODO check min max
                pass
            return True
        except ValueError:
            return False

    def _validate_input_select(self, the_input, value):
        assert the_input.type == waves.const.TYPE_LIST
        self.specific_message = 'allowed values are %s' % str([e[1] for e in the_input.get_choices()])
        return any(e[0] == value for e in the_input.get_choices())

    def _validate_input_text(self, the_input, value):
        assert the_input.type == waves.const.TYPE_TEXT
        assert isinstance(value, basestring) or value is None, 'value %s is not a valid string' % value
        self.specific_message = 'value %s is not a valid string' % value
        return True
