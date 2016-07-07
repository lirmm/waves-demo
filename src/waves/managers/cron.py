from __future__ import unicode_literals

import logging
import time

import django.utils.timezone

import waves.const as const
from waves.models import Job
from waves.runners import JobRunner

__all__ = ['treat_queue_jobs', 'prepare_new_jobs', 'launch_prepared_jobs', 'update_running_jobs']
logger = logging.getLogger('queue')


def treat_queue_jobs():
    """
    Very very simple daemon to monitor jobs
    """
    jobs = Job.objects.filter(status__lte=const.JOB_COMPLETED)
    logger.info("Starting queue processing")
    nb_jobs = jobs.count()
    logger.info("Jobs retrieved %i", nb_jobs)
    while nb_jobs > 0:
        for job in jobs:
            runner = job.runner
            logger.debug('[Runner]-------\n%s\n----------------', runner.dump_config())
            try:
                assert isinstance(runner, JobRunner)
                logger.info("Launching Job %s (runner:%s)", job, runner)
                if not runner.connected:
                    runner.connect()
                if job.status == const.JOB_CREATED:
                    runner.prepare_job(job=job)
                    logger.info("[PrepareJob] %s (runner:%s)", job, runner)
                elif job.status == const.JOB_PREPARED:
                    logger.info("[LaunchJob] %s (runner:%s)", job, runner)
                    runner.run_job(job)
                elif job.status == const.JOB_COMPLETED:
                    runner.job_results(job)
                    logger.info("[ResultJob] %s (runner:%s)", job, runner)
                    runner.job_run_details(job)
                else:
                    runner.job_status(job)
                    logger.debug("[RunningJobStatus] %s (runner:%s)", job.get_status_display(), runner)
            except Exception as e:
                logger.error("Error Job %s (runner:%s-state:%s): %s", job, runner, job.get_status_display(), e.message)
        time.sleep(5)
        jobs = Job.objects.filter(status__lte=const.JOB_COMPLETED)
        nb_jobs = jobs.count()
    logger.info('Processing queue ended, no more job :-)')


def prepare_new_jobs():
    jobs = Job.objects.filter(status=const.JOB_CREATED)
    nb_jobs = jobs.count()
    logger.info("Preparing new jobs at %s, retrieved %i", str(django.utils.timezone.now()), nb_jobs)
    for job in jobs:
        runner = job.runner

        runner.prepare_job(job=job)
    return nb_jobs


def launch_prepared_jobs():
    jobs = Job.objects.filter(status=const.JOB_PREPARED)
    nb_jobs = jobs.count()

    for job in jobs:
        try:
            runner = job.runner
            logger.debug('[Runner]-------\n%s\n----------------', runner.dump_config())

            runner.run_job(job)
        except Exception as e:
            logger.error("Error Job %s (runner:%s): %s", job, runner, e.message)
    return nb_jobs


def update_running_jobs():
    # status_=(const.JOB_RUNNING, const.JOB_QUEUED, const.JOB_COMPLETED)
    jobs = Job.objects.filter(status__gte=const.JOB_QUEUED)
    nb_jobs = jobs.count()
    logger.info("Update running jobs status at %s, retrieved %i", str(django.utils.timezone.now()), nb_jobs)
    for job in jobs:
        try:
            runner = job.runner
            logger.debug('[Runner]\n%s', runner.dump_config())
            runner.job_status(job)
        except Exception as e:
            logger.error("Error Job %s (runner:%s): %s", job, runner, e.message)
    return nb_jobs
