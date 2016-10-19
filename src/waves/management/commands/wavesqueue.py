"""
Daemon-ized execution for job queue following.
Allow to start / stop / restart job queue management

"""
from __future__ import unicode_literals

from os.path import join, dirname
import logging
import time

from django.conf import settings
from waves.management.daemon_command import DaemonCommand
import datetime
import waves.const as const
import waves.settings
from waves.models import Job


class Command(DaemonCommand):
    """
    Dedicated command to summarize current WAVES specific settings
    """
    help = 'Managing WAVES job queue'
    SLEEP_TIME = 5
    work_dir = waves.settings.WAVES_DATA_ROOT
    pidfile_path = join(waves.settings.WAVES_DATA_ROOT, 'waves_daemon.pid')
    pidfile_timeout = 5
    log_file = join(waves.settings.WAVES_LOG_ROOT, "waves_queue.log")
    log_level = waves.settings.WAVES_QUEUE_LOG_LEVEL

    def loop_callback(self):
        """
        Very very simple daemon to monitor jobs queue.

        - Retrieve all current non terminated job, and process according to current status.
        - Jobs are run on a stateless process

        .. todo::
            Implement this as separated forked processes for each jobs, inspired by Galaxy queue treatment.

        :return: Nothing
        """
        jobs = Job.objects.prefetch_related('job_inputs').\
            prefetch_related('job_outputs').filter(status__lt=const.JOB_TERMINATED)
        if jobs.count() > 0:
            logging.info("Starting queue process with %i(s) unfinished jobs", jobs.count())
        for job in jobs:
            runner = job.adaptor
            logging.debug('[Runner]-------\n%s\n----------------', runner.dump_config())
            try:
                job.check_send_mail()
                logging.debug("Launching Job %s (adaptor:%s)", job, runner)
                if job.status == const.JOB_CREATED:
                    runner.prepare_job(job=job)
                    logging.debug("[PrepareJob] %s (adaptor:%s)", job, runner)
                elif job.status == const.JOB_PREPARED:
                    logging.debug("[LaunchJob] %s (adaptor:%s)", job, runner)
                    runner.run_job(job)
                else:
                    runner.job_status(job)
                    if job.status == const.JOB_COMPLETED:
                        runner.job_results(job)
                        logging.info("[ResultJob] %s (adaptor:%s)", job, runner)
                        runner.job_run_details(job)
                    logging.debug("[RunningJobStatus] %s (adaptor:%s)", job.get_status_display(), runner)
            except Exception as e:
                logging.error("Error Job %s (adaptor:%s-state:%s): %s", job, runner, job.get_status_display(), e.message)
                if job.nb_retry >= waves.settings.WAVES_JOBS_MAX_RETRY:
                    job.status = const.JOB_ERROR
                    job.message = 'Job error (too many errors) \n%s' % e.message
            finally:
                logging.info("Queue job terminated at: %s", datetime.datetime.now().strftime('%A, %d %B %Y %H:%M:%I'))
                job.save()
                job.check_send_mail()
                runner.disconnect()
        logging.debug('Go to sleep for %i seconds' % self.SLEEP_TIME)
        time.sleep(self.SLEEP_TIME)

    def exit_callback(self):
        """

        :return:
        """
        # TODO mail that daemon has crashed to someone ?
        logging.info("Exit call back")
        pass
