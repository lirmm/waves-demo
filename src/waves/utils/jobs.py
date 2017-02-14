""" Job Utils functions """
from __future__ import unicode_literals

import waves_adaptors.const
import waves_adaptors.const as jobconst


def default_run_details(job):
    """ Get and retriver a JobRunDetails namedtuple with defaults values"""
    return waves_adaptors.base.JobRunDetails(job.id, str(job.slug), job.remote_job_id, job.title, job.exit_code,
                                             job.created,
                                             '', '', '')
