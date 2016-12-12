
from .jobs import JobAdmin, JobHistoryInline, JobInputInline, JobOutputInline
from .runners import RunnerAdmin, RunnerParamInline
from .services import ServiceMetaInline, ServiceAdmin, \
    ServiceCategoryAdmin, ServiceExitCodeInline
from waves.admin.submissions import RelatedInputInline
from .profiles import NewUserAdmin
from .site import WavesSiteAdmin
