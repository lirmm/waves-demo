""" Daemonized WAVES system commands """
from __future__ import unicode_literals
import sys
from django.core.management.base import BaseCommand, CommandError
from waves.management.daemon.runner import DaemonRunner


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
    import logging.config

    # Django command params
    requires_model_validation = True
    # parameters python-daemon app
    stdin_path = '/dev/null'
    stdout_path = '/dev/stdout'
    stderr_path = '/dev/stderr'
    work_dir = './'
    # pid configuration
    pidfile_path = '/tmp/daemon_command.pid'
    pidfile_timeout = 5
    # logs parameters defaults
    log_backup_count = 5
    log_max_bytes = 5 * 1024 * 1024
    log_file = '/tmp/daemon_command.log'
    log_level = logging.WARNING

    def add_arguments(self, parser):
        """
        Add options to daemon command, compatible for Django version >= 1.8
        :param parser: current Command parser
        :return: Nothing
        """
        parser.add_argument('action', choices=('start', 'stop', 'restart', 'status'), action="store",
                            help="Queue action")
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
        """ Main loop executed by daemon """
        raise NotImplementedError('You must implement loop_callback method to define a daemon')

    def exit_callback(self, signal_number, stack_frame):
        """
        Exit callback, called whenever process is manually stopped, or killed elsewhere.
        .. WARNING:
            If you plan to override this function, remember to always call parent method in order to terminate process
        """
        exception = SystemExit(
            "Terminating on signal {signal_number!r}".format(
                signal_number=signal_number))
        raise exception

    def preloop_callback(self):
        """
        Override this method if you want to do initialization before actual daemon process infinite loop
        """
        pass

    def run(self):
        """
        Method called upon 'start' command from daemon manager, must be overriden in actual job daemon subclass
        """
        logging.debug("Starting Daemon...")
        try:
            self.preloop_callback()
            logging.debug("Starting loopback...")
            while True:
                self.loop_callback()
        except (SystemExit, KeyboardInterrupt):
            # Normal exit getting a signal from the parent process
            pass
        except Exception as exc:
            # Something unexpected happened?
            logging.exception("Unexpected Exception %s", exc.message)

    def _set_up_logger(self):
        from logging.handlers import RotatingFileHandler
        handler = RotatingFileHandler(self.log_file, maxBytes=self.log_max_bytes, backupCount=self.log_backup_count)
        formatter = logging.Formatter('[%(asctime)s] %(levelname)s [%(pathname)s] %(message)s')
        handler.setFormatter(formatter)
        logging.getLogger().addHandler(handler)
        logging.getLogger().setLevel(self.log_level)

    def handle(self, **options):
        """
        Handle commands for a daemon (--start|--stop|--restart|--status)
        :param options: list of possible django command options
        :return: Nothing
        """
        try:
            # refactor sys.argv in order to remove the django command and setup action from Django command option
            sys.argv.pop(0)
            sys.argv[1] = options.pop('action')
            self._set_up_logger()
            run = DaemonRunner(self, **options)
            run.do_action()
        except KeyError:
            raise CommandError('You must specify an action with this command')
