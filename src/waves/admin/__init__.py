""" Models admin packages """
from .jobs import JobAdmin, JobHistoryInline, JobInputInline, JobOutputInline
from .runners import RunnerAdmin, RunnerParamInline
from .services import ServiceMetaInline, ServiceAdmin, \
    ServiceCategoryAdmin
from waves.admin.submissions import *
from .config import WavesSiteAdmin

