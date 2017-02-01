""" WAVES specific ADMIN commands """
from __future__ import unicode_literals

import datetime
import os
import sys
import time
import uuid
import json
from itertools import chain
from django.db import (
    DEFAULT_DB_ALIAS, transaction,
)
from shutil import rmtree
from django.core.exceptions import ObjectDoesNotExist
from django.core.management import BaseCommand, CommandError
from django.conf import settings
# from django.utils.six.moves import input
from django.core.urlresolvers import reverse
from rest_framework.exceptions import ValidationError

import waves.adaptors.const
import waves.exceptions
import waves.settings
import waves.adaptors.const as jobconst
from .daemon.command import DaemonCommand
from waves.models import Job
from waves.models.serializers.services import ServiceSerializer

__all__ = ['JobQueueCommand', 'PurgeDaemonCommand', 'InitDbCommand', 'CleanUpCommand', 'ImportCommand',
           'DumpConfigCommand']


def boolean_input(question, default=None):
    """
    Ask for a boolean response from user
    :param question: Question to ask
    :param default: Default answer
    :return: True or False
    :rtype: bool
    """
    result = input("%s: " % question)
    if not result and default is not None:
        return default
    while len(result) < 1 or result[0].lower() not in "yn":
        result = input("Please answer yes(y) or no(n): ")
    return result[0].lower() == "y"


def choice_input(question, choices, default=None):
    """
    Ask user for choice in a list, indexed by integer response

    :param question: The question to ask
    :param choices: List of possible choices
    :return: Selected choice by user
    :rtype: int
    """
    print("%s:" % question)
    for i, choice in enumerate(choices):
        print("-%s) %s" % (i + 1, choice))
    result = input("Select an option: ")
    try:
        value = int(result)
        if 0 < value <= len(choices):
            return value
    except ValueError:
        if default:
            return default
        else:
            return choice_input('Please select a valid value', choices, default)


def text_input(question, default=None):
    result = input("%s (type Enter to keep default): " % question)
    if not result and default is not None:
        return default
    return str(result)


def action_cancelled(out):
    """
    Simply cancel current action, output confirmation
    """
    out.write('Action cancelled.')
    sys.exit(3)


class JobQueueCommand(DaemonCommand):
    """
    Dedicated command to summarize current WAVES specific settings
    """
    help = 'Managing WAVES job queue states'
    SLEEP_TIME = 2
    work_dir = waves.settings.WAVES_DATA_ROOT
    pidfile_path = os.path.join(waves.settings.WAVES_DATA_ROOT, 'waves_queue.pid')
    pidfile_timeout = 5
    log_file = os.path.join(waves.settings.WAVES_LOG_ROOT, "waves_daemon.log")
    log_level = settings.WAVES_QUEUE_LOG_LEVEL

    def loop_callback(self):
        """
        Very very simple daemon to monitor jobs queue.

        - Retrieve all current non terminated job, and process according to current status.
        - Jobs are run on a stateless process

        .. todo::
            Implement this as separated forked processes for each jobs, inspired by Galaxy queue treatment.

        :return: Nothing
        """
        import logging
        jobs = Job.objects.prefetch_related('job_inputs'). \
            prefetch_related('job_outputs').filter(status__lt=waves.adaptors.const.JOB_TERMINATED)
        if jobs.count() > 0:
            logging.info("Starting queue process with %i(s) unfinished jobs", jobs.count())
        for job in jobs:
            runner = job.adaptor
            logging.debug('[Runner]-------\n%s\n----------------', job.adaptor.dump_config())
            try:
                job.check_send_mail()
                logging.debug("Launching Job %s (adaptor:%s)", job, job.adaptor)
                if job.status == waves.adaptors.const.JOB_CREATED:
                    job.run_prepare()
                    # runner.prepare_job(job=job)
                    logging.debug("[PrepareJob] %s (adaptor:%s)", job, job.adaptor)
                elif job.status == waves.adaptors.const.JOB_PREPARED:
                    logging.debug("[LaunchJob] %s (adaptor:%s)", job, job.adaptor)
                    job.run_launch()
                    # runner.run_job(job)
                elif job.status == waves.adaptors.const.JOB_COMPLETED:
                    # runner.job_run_details(job)
                    job.run_results()
                    logging.debug("[JobExecutionEnded] %s (adaptor:%s)", job.get_status_display(), job.adaptor)
                else:
                    job.run_status()
                    # runner.job_status(job)
            except waves.exceptions.WavesException as e:
                logging.error("Error Job %s (adaptor:%s-state:%s): %s", job, runner, job.get_status_display(),
                              e.message)
                if job.nb_retry >= waves.settings.WAVES_JOBS_MAX_RETRY:
                    job.error(message='Job error (too many errors) \n%s' % e.message)
            finally:
                logging.info("Queue job terminated at: %s", datetime.datetime.now().strftime('%A, %d %B %Y %H:%M:%I'))
                # job.save()
                job.check_send_mail()
                # runner.disconnect()
        logging.debug('Go to sleep for %i seconds' % self.SLEEP_TIME)
        time.sleep(self.SLEEP_TIME)


class PurgeDaemonCommand(DaemonCommand):
    help = 'Clean up old jobs '
    SLEEP_TIME = 86400
    work_dir = waves.settings.WAVES_DATA_ROOT
    pidfile_path = os.path.join(waves.settings.WAVES_DATA_ROOT, 'waves_clean.pid')
    log_file = os.path.join(waves.settings.WAVES_LOG_ROOT, "waves_daemon.log")
    log_level = 'WARNING'

    def loop_callback(self):
        import logging
        logging.info("Purge job launched at: %s", datetime.datetime.now().strftime('%A, %d %B %Y %H:%M:%I'))
        date_anonymous = datetime.date.today() - datetime.timedelta(waves.settings.WAVES_KEEP_ANONYMOUS_JOBS)
        date_registered = datetime.date.today() - datetime.timedelta(waves.settings.WAVES_KEEP_REGISTERED_JOBS)
        anonymous = Job.objects.filter(client__isnull=True, updated__lt=date_anonymous)
        registered = Job.objects.filter(client__isnull=False, updated__lt=date_registered)
        for job in list(chain(*[anonymous, registered])):
            logging.info('Deleting job %s created on %s', job.slug, job.created)
            job.delete()
        logging.info("Purge job terminated at: %s", datetime.datetime.now().strftime('%A, %d %B %Y %H:%M:%I'))


class InitDbCommand(BaseCommand):
    """ Initialise WAVES DB"""
    help = "Init DB data - :WARNING: reset data to its origin"

    def handle(self, *args, **options):
        """ Handle InitDB command """
        from waves.models import Service, Runner, WavesSite, ServiceCategory
        from bootstrap_themes import available_themes
        process = True
        if Service.objects.all().count() > 0 or Runner.objects.all().count() > 0:
            self.stdout.write(self.style.WARNING('Warning, this action reset ALL waves data to initial'))
            process = False
            if boolean_input("Do you want to proceed ? [y/N]", False):
                process = True
        if process:
            # Delete all WAVES data
            ServiceCategory.objects.all().delete()
            Service.objects.all().delete()
            Runner.objects.all().delete()
            WavesSite.objects.all().delete()
            Job.objects.all().delete()
            try:
                self.stdout.write("Configuring WAVES site:")
                site_url = text_input('Your host url (def:http://127.0.0.1)', 'http://127.0.0.1')
                site_name = text_input('Your host name (def:Local WAVES site)', 'Local WAVES site')
                site_theme = choice_input('Choose your bootstrap theme (def:%s)' % settings.WAVES_BOOTSTRAP_THEME,
                                          choices=[theme[1] for theme in available_themes],
                                          default=6)
                from django.contrib.sites.models import Site
                from django.contrib.sites.managers import CurrentSiteManager
                if not getattr(settings, 'SITE_ID', False):
                    raise CommandError('You must set a default SITE ID in your conf. ')
                current_site = Site.objects.get_current()
                current_site.domain = site_url
                current_site.name = site_name
                current_site.save()
                WavesSite.objects.create(site=current_site, theme=available_themes[site_theme - 1][0])
                self.stdout.write("... Done")
                if boolean_input('Do you want to init your job runners ? [y/N]', False):
                    self.stdout.write('Creating runners ...')
                    from waves.utils.runners import get_runners_list
                    for runner_clazz in get_runners_list(raw=True):
                        Runner.objects.create(runner=runner_clazz, description='Runner Adaptor: %s' % runner_clazz)
                    self.stdout.write("... Done")

                # TODO add ask for import sample services ?
                if boolean_input("Do you wan to load sample services categories ? [y/N]", False):
                    self.stdout.write('Loading sample categories ...')
                    from django.core.management import call_command
                    call_command('loaddata', 'waves', 'waves/fixtures/sample_categories.json')
                    self.stdout.write("... Done")
                self.stdout.write('Your WAVES data are ready :-)')
            except Exception as exc:
                self.stderr.write('Error occurred, you database may be inconsistent ! \n %s - %s ' % (
                    exc.__class__.__name__, str(exc)))
        else:
            action_cancelled(self.stdout)


class CleanUpCommand(BaseCommand):
    """ Clean up file system according to jobs in database """
    help = "Clean up inconsistent data on disk related to jobs"

    # args = '[--from-date date] to limit clean up until date'
    def print_file_error(self, islink, path, exe_info):
        self.stderr.write("Unable to remove dir %s (%s)" % (path, exe_info))

    def add_arguments(self, parser):
        parser.add_argument('--to-date', default=None, help="Restrict purge to a date (anterior)")

    def handle(self, *args, **options):
        removed = []
        for dir_name in os.listdir(waves.settings.WAVES_JOB_DIR):
            try:
                # DO nothing, job exists in DB
                Job.objects.get(slug=uuid.UUID('{%s}' % dir_name))
            except ObjectDoesNotExist:
                removed.append(str(dir_name))
            except ValueError:
                pass
        if len(removed) > 0:
            choice = choice_input(
                "%i directory(ies) to be deleted, this operation is not reversible, are you sure ?"
                % len(removed), choices=[
                    "List directories to delete",
                    "Perform delete",
                    "Cancel"
                ])

            if choice == 1:
                self.stdout.write("Directories to delete: ")
                for dir_name in removed:
                    self.stdout.write(os.path.join(waves.settings.WAVES_JOB_DIR, dir_name))
            elif choice == 2:
                for dir_name in removed:
                    self.stdout.write('Removed directory: %s' % dir_name)
                    # onerror(os.path.islink, path, sys.exc_info())
                    rmtree(os.path.join(waves.settings.WAVES_JOB_DIR, dir_name),
                           onerror=self.print_file_error)
            else:
                action_cancelled(self.stdout)
        else:
            self.stdout.write("Your jobs data dir is sane, nothing wrong here")


class ImportCommand(BaseCommand):
    """ Load and create a new service from a previously exported service from WAVES backoffice """
    help = "Load a previously exported service into your WAVES instance"

    def add_arguments(self, parser):
        parser.add_argument('type_model', type=str, action="store",
                            choices=('service', 'runner'),
                            help="Type of data to import (service, runner)")
        parser.add_argument('args', metavar='export_id', nargs='+', help='Previously exported data.')
        parser.add_argument('--skip_category', action='store_true', dest="skip_cat", default=False,
                            help="Skip import service category")
        parser.add_argument('--skip_runner', action='store_true', dest="skip_run", default=False,
                            help="Skip import service runner")
        parser.add_argument('--database', action='store', dest='database',
                            default=DEFAULT_DB_ALIAS, help='Nominates a specific database to load '
                                                           'fixtures into. Defaults to the "default" database.')

    def handle(self, *args, **options):
        """ Handle import for services """
        # TODO handle single Runner / import export
        exported_files = []
        type_mode = options.get('type_model', 'service')
        if type_mode != 'service':
            raise CommandError('Sorry, only services can be imported for the moment')
        for export in args:
            exported_files.append(self.find_export_files(export, type_mode))
        self.using = options.get('database')
        for exported_file in exported_files:
            with transaction.atomic(using=self.using) and open(exported_file) as fp:
                json_srv = json.load(fp)
                if type_mode == 'service':
                    serializer = ServiceSerializer(data=json_srv, skip_cat=options.get('skip_cat'),
                                                   skip_run=options.get('skip_run'))
                else:
                    raise NotImplementedError('Currently only services can be imported')
                try:
                    db_version = json_srv.pop('db_version', None)
                    if db_version != waves.settings.WAVES_DB_VERSION:
                        raise ValidationError(
                            'DB version are not compatible %s (expected %s) - Consider upgrading your database' % (
                                db_version, waves.settings.WAVES_DB_VERSION))
                    if serializer.is_valid(raise_exception=True):
                        self.stdout.write("Service import from file %s ...." % exported_file)
                        serializer.validated_data['name'] += ' (Import)'
                        new_serv = serializer.save()
                        self.stdout.write(' > new service : %s' % new_serv)
                        self.stdout.write(
                            "... Done, you may edit service on: [your_waves_admin_host]%s " % reverse(
                                'admin:waves_service_change',
                                args=[new_serv.id]))
                except ValidationError as exc:
                    self.stderr.write('Data can not be import: %s' % exc.detail)
                except AssertionError as exc:
                    self.stderr.write('Data import error %s' % exc)

    def find_export_files(self, export, type_model):
        file_name = '%s_%s.json' % (type_model, export)
        export_file = os.path.join(settings.WAVES_DATA_ROOT, file_name)
        if os.path.isfile(export_file):
            return export_file
        else:
            raise CommandError("Unable to find exported file: %s, are they in your data root (%s)? " % (
                file_name, settings.WAVES_DATA_ROOT))


class DumpConfigCommand(BaseCommand):
    """
    Dedicated command to summarize current WAVES specific settings
    """
    help = 'Dump all WAVES configuration setup'

    def handle(self, *args, **options):
        """
        Handle command in Django command line interface
        Print out to standard output current WAVES configuration.

        :param args: Command arguments (expected none)
        :param options: Command options (expected none)
        """
        import waves.settings
        from django.conf import settings
        var_dict = vars(waves.settings)
        self.stdout.write("*******************************")
        self.stdout.write("****  WAVES current setup *****")
        self.stdout.write("*******************************")
        self.stdout.write('Current Django default database: %s' % settings.DATABASES['default'])
        self.stdout.write('Current Django static files dirs: %s' % settings.STATICFILES_DIRS)
        self.stdout.write('Current Django static root path: %s' % settings.STATIC_ROOT)
        self.stdout.write('Current Django media root path: %s' % settings.MEDIA_ROOT)
        self.stdout.write('Current Django allowed hosts: %s' % settings.ALLOWED_HOSTS)
        self.stdout.write("*******************************")
        for key in sorted(var_dict.keys()):
            if key.startswith('WAVES'):
                self.stdout.write('%s: %s' % (key, var_dict[key]))
        self.stdout.write("*******************************")
