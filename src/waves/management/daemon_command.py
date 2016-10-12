from __future__ import unicode_literals
import signal
import sys

from django.core.management.base import BaseCommand, CommandError

from waves.management.daemon_runner import DaemonRunner
import logging


class DaemonCommand(BaseCommand):
    """
    Run a management command as a daemon.

    Subclass this and override the `loop_callback` method with the code the 
    daemon process should run. Optionally, override `exit_callback` with 
    code to run when the process is stopped.

    Alternatively, if your code has more complex setup/shutdown requirements,
    override `handle_noargs` along the lines of the basic version here. 
    
    Pass one of --start, --stop, --restart or --status to work as a daemon.
    Otherwise, the command will run as a standard application.
    """
    requires_model_validation = True
    stdin_path = '/dev/null'
    stdout_path = '/dev/null'
    stderr_path = '/dev/null'
    work_dir = '/'
    pidfile_path = '/tmp/daemon_command.pid'
    pidfile_timeout = 5
    log_file = '/tmp/daemon_command.log'
    log_level = logging.INFO

    def add_arguments(self, parser):
        """
        Add options to daemon command, compatible for Django version >= 1.8
        :param parser: current Command parser
        :return: Nothing
        """
        parser.add_argument('--start', action='store_const', const='start', dest='action', help='Start the daemon')
        parser.add_argument('--stop', action='store_const', const='stop', dest='action', help='Stop the daemon')
        parser.add_argument('--restart', action='store_const', const='restart', dest='action',
                            help='Stop and restart the daemon')
        parser.add_argument('--status', action='store_const', const='status', dest='action',
                            help='Report whether the daemon is currently running or stopped')
        parser.add_argument('--workdir', action='store', dest='work_dir', help='Setup daemon working dir',
                            default=self.work_dir)
        parser.add_argument('--pidfile', action='store', dest='pidfile_path', default=self.pidfile_path,
                            help='PID absolute filename.')
        parser.add_argument('--logfile', action='store', dest='log_file', default=self.log_file,
                            help='Path to log file')
        parser.add_argument('--stdout', action='store', dest='stdout', default=self.stdout,
                            help='Destination to redirect standard out')
        parser.add_argument('--stderr', action='store', dest='stderr', default=self.stderr,
                            help='Destination to redirect standard error')
        parser.add_argument('--verbose', action='store', dest='verbose', default=True, type=bool,
                            help='Verbose, or not')

    def loop_callback(self):
        raise NotImplementedError('You must implement loop_callback method to define a daemon')

    def exit_callback(self):
        """
        Extra code run each time process shutdown
        :return:
        """
        pass

    def run(self):
        """
        Method called upon 'start' command from daemon manager, must be overriden in actual job daemon subclass
        :raise: NotImplementedError
        """
        logging.basicConfig(format="%(asctime)s [%(processName)s] %(levelname)s %(message)s",
                            filename=self.log_file,
                            level=self.log_level)
        logging.info("Starting...")
        try:
            while True:
                self.loop_callback()
        except (SystemExit, KeyboardInterrupt):
            # Normal exit getting a signal from the parent process
            pass
        except Exception as exc:
            # Something unexpected happened?
            logging.exception("Unexpected Exception %s", exc.message)
        finally:
            logging.info('Finishing job, clean up the mess...')
            self.exit_callback()

    def handle(self, **options):
        """
        Handle commands for a daemon (start|stop|restart|status)
        :param options: list of possible django command options
        :return: Nothing
        """
        try:
            action = options.pop('action', None)
            signal.signal(signal.SIGTERM, lambda sig, frame: self.exit_callback())
            run = DaemonRunner(self, argv=[sys.argv[1], action], **options)
            run.do_action()
        except KeyError:
            raise CommandError('You must specify an action with this command')


