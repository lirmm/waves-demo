"""
WAVES jobs constants
--------------------
"""
from __future__ import unicode_literals

#: JOB status : Unknown (yes sometimes it happens)
from collections import namedtuple

JOB_UNDEFINED = -1
#: JOB status 'Created'
JOB_CREATED = 0
#: JOB status 'Prepared'
JOB_PREPARED = 1
#: JOB status 'Queued'
JOB_QUEUED = 2
#: JOB status 'Running (remotely)'
JOB_RUNNING = 3
#: JOB status 'Suspended (remotly)'
JOB_SUSPENDED = 4
#: JOB status 'Completed' (results are being retrieved)
JOB_COMPLETED = 5
#: JOB status 'Done' results are available on WAVES
JOB_TERMINATED = 6
#: Job status 'Cancelled' at least locally, remotely if possible
JOB_CANCELLED = 7
JOB_ERROR = 9

STR_JOB_UNDEFINED = 'Unknown'
STR_JOB_CREATED = 'Created'
STR_JOB_PREPARED = 'Prepared for run'
STR_JOB_QUEUED = 'Queued'
STR_JOB_RUNNING = 'Running'
STR_JOB_COMPLETED = 'Completed'
STR_JOB_TERMINATED = 'Finished'
STR_JOB_CANCELLED = 'Cancelled'
STR_JOB_SUSPENDED = 'Suspended'
STR_JOB_ERROR = 'In Error'

STATUS_LIST = (
    (JOB_UNDEFINED, STR_JOB_UNDEFINED),
    (JOB_CREATED, STR_JOB_CREATED),
    (JOB_PREPARED, STR_JOB_PREPARED),
    (JOB_QUEUED, STR_JOB_QUEUED),
    (JOB_RUNNING, STR_JOB_RUNNING),
    (JOB_SUSPENDED, STR_JOB_SUSPENDED),
    (JOB_COMPLETED, STR_JOB_COMPLETED),
    (JOB_TERMINATED, STR_JOB_TERMINATED),
    (JOB_CANCELLED, STR_JOB_CANCELLED),
    (JOB_ERROR, STR_JOB_ERROR),
)

NEXT_STATUS = {
    JOB_CREATED: JOB_PREPARED,
    JOB_PREPARED: JOB_QUEUED,
    JOB_QUEUED: JOB_RUNNING,
    JOB_RUNNING: JOB_COMPLETED,
    JOB_COMPLETED: JOB_TERMINATED
}
JobRunDetails = namedtuple("JobRunDetails",
                           ['internal_id', 'slug', 'job_remote_id', 'name', 'exit_code', 'created', 'started',
                            'finished', 'extra'])
ImportService = namedtuple("ImportService",
                           ['name', 'version', 'short_description', 'wrapped'])
