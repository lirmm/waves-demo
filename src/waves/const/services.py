"""
WAVES Services constants
------------------------
"""
from __future__ import unicode_literals

#: Service status 'Draft', i.e only accessible by creator (staff member)
SRV_DRAFT = 0
# restricted to staff
#: Service status 'Test', i.e only accessible by staff user (Django flag is_staff)
SRV_TEST = 1
# restricted to logged in users with
#: Service status 'Restricted', i.e  accessible by staff + designated registered user
SRV_RESTRICTED = 2

# publicly available
#: Service status 'Public', i.e service is online and accessible to everyone
SRV_PUBLIC = 3


SRV_STATUS_LIST = [
    [SRV_DRAFT, 'Draft'],
    [SRV_TEST, 'Test'],
    [SRV_RESTRICTED, 'Restricted'],
    [SRV_PUBLIC, 'Public'],
]

#: Service Input Type 'boolean': check if submitted values are boolean
TYPE_BOOLEAN = 'boolean'
#: Service Input Type 'File': check if submitted values are files (or content to write to file)
TYPE_FILE = 'file'
#: Service Input Type 'List of choices': check if submitted values are in specified list
TYPE_LIST = 'list'
#: Service Input Type 'integer': check if input type is a integer
TYPE_NUMBER = 'number'
#: Service Input Type 'text': no special check, except when used in outputs name, normalized value is stored
TYPE_TEXT = 'text'

IN_TYPE = [
    (TYPE_FILE, 'Input file'),
    (TYPE_LIST, 'List of values'),
    (TYPE_BOOLEAN, 'Boolean'),
    (TYPE_NUMBER, 'Number'),
    (TYPE_TEXT, 'Text')
]
#: Service Input Command line parameter type 'valuated' i.e: --param_name=value
OPT_TYPE_VALUATED = 1
#: Service Input Command line parameter type 'simple' i.e: -param_name value
OPT_TYPE_SIMPLE = 2
#: Service Input Command line parameter type 'option' i.e: -param_name
OPT_TYPE_OPTION = 3
#: Service Input Command line parameter type 'posix' i.e: just value (in right place)
OPT_TYPE_POSIX = 4
#: Service Input Command line parameter type 'named option' i.e: --param_name
OPT_TYPE_NAMED_OPTION = 5

OPT_TYPE = [
    (OPT_TYPE_VALUATED, 'Valuated param (--param_name=value)'),
    (OPT_TYPE_SIMPLE, 'Simple param (-param_name value)'),
    (OPT_TYPE_OPTION, 'Option param (-param_name)'),
    (OPT_TYPE_NAMED_OPTION, 'Option named param (--param_name)'),
    (OPT_TYPE_POSIX, 'Positional param (no name)')
]

DISPLAY_SELECT = 'select'
DISPLAY_RADIO = 'radio'
DISPLAY_CHECKBOX = 'checkbox'
LIST_DISPLAY_TYPE = [
    (DISPLAY_SELECT, 'Select List'),
    (DISPLAY_RADIO, 'Radio buttons'),
    (DISPLAY_CHECKBOX, 'Check box')
]

OUT_TYPE = (
    ('stout', 'Standard output'),
    ('file', 'Output file')
)
