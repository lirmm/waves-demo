from __future__ import unicode_literals
import logging.config
import time
import datetime
from itertools import chain
from waves.models import JobAdminHistory
import waves.const as const
import waves.settings
from waves.models import Job

__all__ = ['treat_queue_jobs', 'purge_old_jobs']
logger = logging.getLogger(__name__)


def treat_queue_jobs():
    """
    Very very simple daemon to monitor jobs
    """
    logger.info("Queue job launched at: %s", datetime.datetime.now().strftime('%A, %d %B %Y %H:%M:%I'))
    while True:
        jobs = Job.objects.filter(status__lt=const.JOB_TERMINATED)
        if jobs.count() == 0:
            break
        logger.info("Starting queue process with %i(s) unfinished jobs", jobs.count())
        for job in jobs:
            runner = job.runner
            logger.debug('[Runner]-------\n%s\n----------------', runner.dump_config())
            try:
                logger.info("Launching Job %s (runner:%s)", job, runner)
                if job.status == const.JOB_CREATED:
                    job.check_send_mail()
                    runner.prepare_job(job=job)
                    job.nb_retry = 0
                    logger.info("[PrepareJob] %s (runner:%s)", job, runner)
                elif job.status == const.JOB_PREPARED:
                    logger.info("[LaunchJob] %s (runner:%s)", job, runner)
                    runner.run_job(job)
                    job.nb_retry = 0
                elif job.status == const.JOB_COMPLETED:
                    runner.job_results(job)
                    logger.info("[ResultJob] %s (runner:%s)", job, runner)
                    runner.job_run_details(job)
                    job.nb_retry = 0
                else:
                    runner.job_status(job)
                    job.nb_retry = 0
                    logger.debug("[RunningJobStatus] %s (runner:%s)", job.get_status_display(), runner)
            except Exception as e:
                logger.error("Error Job %s (runner:%s-state:%s): %s", job, runner, job.get_status_display(), e.message)
                job.job_history.add(JobAdminHistory.objects.create(job=job, status=const.JOB_ERROR, message=e.message))
                job.nb_retry += 1
                if job.nb_retry >= waves.settings.WAVES_JOBS_MAX_RETRY:
                    job.status = const.JOB_CANCELLED
                    job.message = 'Job Automatically Cancelled (max retry reached) \n%s' % e.message
                break
            finally:
                logger.info("Queue job terminated at: %s", datetime.datetime.now().strftime('%A, %d %B %Y %H:%M:%I'))
                job.save()
                job.check_send_mail()
                runner.disconnect()
        logger.info('go to sleep for 10 seconds')
        time.sleep(10)


def purge_old_jobs():
    """
    Purge old jobs from db and disk according to settings values (WAVES_KEEP_ANONYMOUS_JOBS, WAVES_KEEP_REGISTERED_JOBS) set in days
    Returns:
        None
    """
    logger.info("Purge job launched at: %s", datetime.datetime.now().strftime('%A, %d %B %Y %H:%M:%I'))
    date_anonymous = datetime.date.today() - datetime.timedelta(waves.settings.WAVES_KEEP_ANONYMOUS_JOBS)
    date_registered = datetime.date.today() - datetime.timedelta(waves.settings.WAVES_KEEP_REGISTERED_JOBS)
    anonymous = Job.objects.filter(client__isnull=True, updated_lt=date_anonymous)
    registered = Job.objects.filter(client__isnull=False, updated_lt=date_registered)
    for job in list(chain(*[anonymous, registered])):
        logger.info('Deleting job %s created on %s', job.slug, job.created)
        job.delete()
    logger.info("Purge job terminated at: %s", datetime.datetime.now().strftime('%A, %d %B %Y %H:%M:%I'))
