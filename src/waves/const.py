"""
Constant used in Waves webapps
"""
from __future__ import unicode_literals

META_WEBSITE = 'website'
META_DOC = 'doc'
META_DOWNLOAD = 'download'
META_PAPER = 'paper'
META_MISC = 'misc'
META_CITE = 'cite'
META_CMD_LINE = 'cmd'
META_USER_GUIDE = 'rtfm'
META_FEATURES = 'feat'

SERVICE_META = (
    (META_WEBSITE, 'Dedicated website link'),
    (META_DOC, 'Documentation link'),
    (META_DOWNLOAD, 'Download link'),
    (META_FEATURES, 'Tool features'),
    (META_MISC, 'Miscellaneous'),
    (META_PAPER, 'Related Paper link'),
    (META_CITE, 'Citation'),
    (META_USER_GUIDE, 'User Guide'),
    (META_CMD_LINE, 'Command line')
)

JOB_UNDEFINED = -1
JOB_CREATED = 0
JOB_PREPARED = 1
JOB_QUEUED = 2
JOB_RUNNING = 3
JOB_SUSPENDED = 4
JOB_COMPLETED = 5
JOB_TERMINATED = 6
JOB_CANCELLED = 7
JOB_ERROR = 9

STR_JOB_UNDEFINED = 'Unknown'
STR_JOB_CREATED = 'Created'
STR_JOB_PREPARED = 'Prepared for run'
STR_JOB_QUEUED = 'Queued'
STR_JOB_RUNNING = 'Running'
STR_JOB_COMPLETED = 'Completed'
STR_JOB_TERMINATED = 'Done'
STR_JOB_CANCELLED = 'Cancelled'
STR_JOB_SUSPENDED = 'Suspended'
STR_JOB_ERROR = 'In Error'

STATUS_LIST = [
    [JOB_UNDEFINED, STR_JOB_UNDEFINED],
    [JOB_CREATED, STR_JOB_CREATED],
    [JOB_QUEUED, STR_JOB_QUEUED],
    [JOB_PREPARED, STR_JOB_PREPARED],
    [JOB_RUNNING, STR_JOB_RUNNING],
    [JOB_TERMINATED, STR_JOB_TERMINATED],
    [JOB_COMPLETED, STR_JOB_COMPLETED],
    [JOB_CANCELLED, STR_JOB_CANCELLED],
    [JOB_SUSPENDED, STR_JOB_SUSPENDED],
    [JOB_ERROR, STR_JOB_ERROR]
]

# only accessed by creator
SRV_DRAFT = 0
# restricted to _staff flagged members
SRV_TEST = 1
# restricted to staff + authorized user from list
SRV_RESTRICTED = 2
# publicly available
SRV_PUBLIC = 3

SRV_STATUS_LIST = [
    [SRV_DRAFT, 'Draft'],
    [SRV_TEST, 'Test'],
    [SRV_RESTRICTED, 'Restricted'],
    [SRV_PUBLIC, 'Public'],
]

TYPE_BOOLEAN = 'boolean'
TYPE_FILE = 'file'
TYPE_LIST = 'select'
TYPE_INTEGER = 'number'
TYPE_FLOAT = 'float'
TYPE_TEXT = 'text'

IN_TYPE = (
    (TYPE_FILE, 'Input file'),
    (TYPE_LIST, 'List of values'),
    (TYPE_BOOLEAN, 'Boolean'),
    (TYPE_INTEGER, 'Integer'),
    (TYPE_FLOAT, 'Float'),
    (TYPE_TEXT, 'Text')
)

OPT_TYPE_NONE = 0
OPT_TYPE_VALUATED = 1
OPT_TYPE_SIMPLE = 2
OPT_TYPE_OPTION = 3
OPT_TYPE_POSIX = 4
OPT_TYPE_NAMED_OPTION = 5

OPT_TYPE = (
    (OPT_TYPE_NONE, 'Not used in job submission'),
    (OPT_TYPE_VALUATED, 'Valuated param (--param_name=value)'),
    (OPT_TYPE_SIMPLE, 'Simple param (-param_name value)'),
    (OPT_TYPE_OPTION, 'Option param (-param_name)'),
    (OPT_TYPE_NAMED_OPTION, 'Option named param (--param_name)'),
    (OPT_TYPE_POSIX, 'Positional param (no name)')
)

DISPLAY_SELECT = 'select'
DISPLAY_RADIO = 'radio'
DISPLAY_CHECKBOX = 'checkbox'
LIST_DISPLAY_TYPE = (
    (DISPLAY_SELECT, 'Select List'),
    (DISPLAY_RADIO, 'Radio buttons'),
    (DISPLAY_CHECKBOX, 'Check box')
)

OUT_TYPE = (
    ('stout', 'Standard output'),
    ('file', 'Output file')
)
