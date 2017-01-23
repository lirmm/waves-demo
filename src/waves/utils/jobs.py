import waves.const


def default_run_details(job):
    return waves.const.JobRunDetails(job.id, str(job.slug), job.remote_job_id, job.title, job.exit_code, job.created,
                                     '', '', '')