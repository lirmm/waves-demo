from __future__ import unicode_literals

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

"""
Dynamic inputs fields validation for job creation
TYPE_BOOLEAN = 'boolean'
TYPE_FILE = 'file'
TYPE_LIST = 'select'
TYPE_INTEGER = 'int'
TYPE_FLOAT = 'float'
TYPE_TEXT = 'text'
"""


def validate_input(the_input, value):
    import sys
    try:
        func = getattr(sys.modules[__name__], 'validate_input_' + the_input.type)
        if not func(the_input, value):
            raise ValidationError('Input %s is not a valid %s' % (the_input, the_input.type))
    except AttributeError:
        raise ValidationError('No Validator found for input:%s - type:%s' % (the_input, the_input.type))


def validate_input_boolean(the_input, value):
    # Add check format values
    return value.lower() in ("yes", "true", "1", 'no', 'false', '0', 'none')


def validate_input_file(the_input, value):
    with open(the_input.file_path, 'r'):
        return True
    return False


def validate_input_int(the_input, value):
    try:
        int(value)
        if getattr(the_input, 'format', False):
            # check min max ?
            pass
        return True
    except ValueError:
        return False


def validate_input_float(the_input, value):
    try:
        float(value)
        if getattr(the_input, 'format', False):
            # check min max ?
            pass
        return True
    except ValueError:
        return False


def validate_input_select(the_input, value):
    if getattr(the_input, 'get_choices', False):
        if the_input.get_choices() and not any(e == value for e, _ in the_input.get_choices()[1]):
            return False
    return True


def validate_input_text(the_input, value):
    return True
