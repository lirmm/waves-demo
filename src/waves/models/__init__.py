""" All WAVES related models imports """
from __future__ import unicode_literals

from .base import *
from .adaptors import *
from .runners import *
from .services import *
from .jobs import *
from .config import *
from .submissions import *
from .inputs import *
from .metas import *

"""
List of different constants used for models
"""


OUT_TYPE = (
    ('stout', 'Standard output'),
    ('file', 'Output file')
)
