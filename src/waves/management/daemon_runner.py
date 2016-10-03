"""
Extended DaemonRunner class (from python-daemon):
- add `status` command
- add `argv` override to __init__ arguments
- implement base `run()` method, which launch `loop_callback()`, on exit run `exit_callback()`

"""
from os import kill
import lockfile
from daemon import DaemonContext
from daemon.runner import DaemonRunner as BaseDaemonRunner, DaemonRunnerStopFailureError, \
    DaemonRunnerStartFailureError, make_pidlockfile, emit_message


class DaemonRunner(BaseDaemonRunner):
    """ Override base DaemonRunner from python-daemon in order to add 'Status' method

    """
    LOCK_ERROR = "Unable to acquire lock: process may be already running ?"
    START_ERROR = "Unable to start %s"
    STOP_ERROR = "Unable to stop %s"
    STATUS_STOPPED = "Stopped"
    STATUS_RUNNING = "Running"

    def _status(self):
        try:
            pid = self.pidfile.read_pid()
            kill(pid, 0)
        except (OSError, TypeError):
            emit_message("Stopped")
            return self.STATUS_STOPPED
        else:
            emit_message("Running")
            return self.STATUS_RUNNING

    def _start(self):
        try:
            super(DaemonRunner, self)._start()
        except DaemonRunnerStartFailureError as exc:
            emit_message(self.START_ERROR % exc.message)
        except lockfile.LockTimeout as exc:
            emit_message(self.LOCK_ERROR)

    def _stop(self):
        try:
            super(DaemonRunner, self)._stop()
        except DaemonRunnerStopFailureError as exc:
            emit_message(self.STOP_ERROR % exc.message)

    def _restart(self):
        super(DaemonRunner, self)._restart()

    action_funcs = {
        'start': _start,
        'stop': _stop,
        'restart': _restart,
        'status': _status
    }

    def __init__(self, app, argv=None, work_dir='/', chroot=None, umask=0, log_file=None, **kwargs):
        """ Set up the parameters of a new runner.
            **Override base DaemonRunner in order to provide specific args upon creation**

            :param:
            :param app: The application instance; see below.
            :return: ``None``.

            The `app` argument must have the following attributes:

            * `stdin_path`, `stdout_path`, `stderr_path`: Filesystem paths
              to open and replace the existing `sys.stdin`, `sys.stdout`,
              `sys.stderr`.

            * `pidfile_path`: Absolute filesystem path to a file that will
              be used as the PID file for the daemon. If ``None``, no PID
              file will be used.

            * `pidfile_timeout`: Used as the default acquisition timeout
              value supplied to the runner's PID lock file.

            * `run`: Callable that will be invoked when the daemon is
              started.

            """
        self.parse_args(argv)
        self.app = app
        self.daemon_context = DaemonContext()
        self.daemon_context.stdin = open(app.stdin_path, 'rt')
        self.daemon_context.stdout = open(app.stdout_path, 'w+t')
        self.daemon_context.stderr = open(app.stderr_path, 'w+t', buffering=0)
        self.daemon_context.working_directory = work_dir
        self.daemon_context.chroot_directory = chroot
        self.daemon_context.umask = umask
        self.daemon_context.detach_process = True
        self.pidfile = make_pidlockfile(app.pidfile_path, app.pidfile_timeout) if app.pidfile_path is not None else None
        if log_file is not None:
            self.daemon_context.files_preserve = [log_file]
        self.daemon_context.pidfile = self.pidfile
        self.exit_callback = exit
