from __future__ import unicode_literals

from django.core.management.base import BaseCommand, CommandError
from django.utils.six.moves import input
from django.core.exceptions import ObjectDoesNotExist
import os
import sys
import uuid
from shutil import rmtree
from waves.models import Job
import waves.settings


class Command(BaseCommand):
    """ WAVES dedicated administration Django command line interface (./manage.py)
    """
    help = 'WAVES Administration commands'
    command_list = ['clean_up', 'config', 'init_db']

    def print_file_error(self, islink, path, exe_info):
        self.stderr.write("Unable to remove dir %s (%s)" % (path, exe_info))

    def add_arguments(self, parser):
        parser.add_argument('command', choices=self.command_list)
        parser.add_argument(
            '--from_date',
            default=None
        )

    def handle(self, *args, **options):
        """
        Handle command line arguments and processes to launch

        - **Possible actions**:
            - *clean_up* : clean_up job working dirs, deleting those not related to Job models in DB
            - *init_db* : initialize data from sample data, erase current if needed
            - ...

        .. todo:
            Add more commands :-)
            - 'run_job' followed by job id or slug.
            - 'cancel_job' followed by job id or slug.
            - 'kill_cron' : should kill current crontable processes, deactivation crontab at the same time
            - ...

        :param args: Command arguments
        :param options: Command options
        :return: None
        """
        if options['command'] == 'clean_up':
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
                choice = 1
                while choice not in [2, 3]:
                    choice = self._choice_input(
                        "This will erase %i directory, this operation is not reversible, are you sure ? [y/N]"
                        % len(removed), choices=[
                            "List directories to delete",
                            "Perform delete",
                            "Cancel"
                        ])
                    if choice == 1:
                        self.stdout.write("Directories to delete:")
                        for dir_name in removed:
                            self.stdout.write(os.path.join(waves.settings.WAVES_JOB_DIR, dir_name))
                    elif choice == 2:
                        for dir_name in removed:
                            self.stdout.write('Removed %s' % dir_name)
                            # onerror(os.path.islink, path, sys.exc_info())
                            rmtree(os.path.join(waves.settings.WAVES_JOB_DIR, dir_name), ignore_errors=False,
                                   onerror=self.print_file_error)
                    else:
                        self._action_cancelled()
                        sys.exit(3)
            else:
                self.stdout.write("Your data dir is sane, nothing wrong found")
        elif options['command'] == 'init_db':
            self.stderr.write('Warning, this action reset ALL waves data to initial')
            if self._boolean_input("Do you want to proceed ? [y/N]"):
                from django.contrib.auth import get_user_model
                from waves.models import Service, APIProfile, Runner
                for service in Service.objects.all():
                    service.delete()
                User = get_user_model()
                for profile in User.objects.all():
                    profile.delete()
                for runner in Runner.objects.all():
                    runner.delete()
                from django.core.management import call_command
                try:
                    call_command('loaddata', 'waves', 'waves/fixtures/init.json')
                    self.stdout.write("Reset Done")
                except Exception as exc:
                    self.stderr.write('Error occurred, you database may be inconsistent ! \n %s - %s ' % (exc.__class__.__name__, str(exc)))
            else:
                self._action_cancelled()
        elif options['command'] in self.command_list:
            self.stderr.write('This function is not yet implemented, sorry')
        else:
            self.stderr.write('This function doest not exists')
            self.stdout.write(self.help)

    def _action_cancelled(self):
        """
        Simply cancel current action, output confirmation
        """
        self.stdout.write('Action cancelled.')

    @staticmethod
    def _boolean_input(question, default=None):
        """
        Ask for a boolean response from user
        :param question: Question to ask
        :param default: Default answer
        :return: True or False
        :rtype: bool
        """
        result = input("%s " % question)
        if not result and default is not None:
            return default
        while len(result) < 1 or result[0].lower() not in "yn":
            result = input("Please answer yes(y) or no(n): ")
        return result[0].lower() == "y"

    @staticmethod
    def _choice_input(question, choices):
        """
        Ask user for choice in a list, indexed by integer response

        :param question: The question to ask
        :param choices: List of possible choices
        :return: Selected choice by user
        :rtype: int
        """
        print(question)
        for i, choice in enumerate(choices):
            print(" %s) %s" % (i + 1, choice))
        result = input("Select an option: ")
        while True:
            try:
                value = int(result)
                if 0 < value <= len(choices):
                    return value
            except ValueError:
                pass
        result = input("Please select a valid option: ")
