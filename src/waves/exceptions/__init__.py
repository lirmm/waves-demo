# -*- coding: utf-8
import logging

__all__ = ['RunnerException', 'RunnerNotInitialized', 'RunnerNotReady', 'RunnerConnectionError',
           'JobException', 'JobInconsistentStateError', 'JobMissingMandatoryParam', 'JobPrepareException',
           'JobRunException', 'JobSubmissionException', 'JobCreateException', 'RunnerUnexpectedInitParam']

logger = logging.getLogger(__name__)


class WavesException(Exception):
    """Waves webapp base exception

    """
    def _log(self):
        logger.fatal('%s: %s ' % (self.__class__.__name__, self.message))

    def __init__(self, *args, **kwargs):
        super(WavesException, self).__init__(*args, **kwargs)
        self._log()


class RunnerException(WavesException):
    """Base Exception class for all Runner related errors
    """
    def __init__(self, *args, **kwargs):
        super(RunnerException, self).__init__(*args, **kwargs)


class RunnerNotInitialized(RunnerException):
    pass


class RunnerUnexpectedInitParam(RunnerException):
    pass


class RunnerConnectionError(RunnerException):
    def __init__(self, reason, msg=''):
        message = reason
        if msg != '':
            message = '%s %s' % (msg, message)
        super(RunnerException, self).__init__(message)


class RunnerNotReady(RunnerException):
    pass


class JobException(WavesException):
    """Base Exception class for all job related errors
    """
    def __init__(self, message, job=None):
        if job is not None:
            # TODO add job things here ?
            pass
        super(JobException, self).__init__(message)


class JobRunException(JobException):
    """More specifically related job run errors"""
    pass


class JobCreateException(JobException):
    def __init__(self, message, job=None):
        if job is not None:
            job.delete_job_dirs()
        super(JobException, self).__init__(message)


class JobSubmissionException(JobCreateException):
    """More specifically related job preparation errors"""
    pass


class JobMissingMandatoryParam(JobSubmissionException):
    def __init__(self, param, job):
        job.delete_job_dirs()
        message = 'Missing mandatory job parameter "%s"' % param
        super(JobException, self).__init__(message, job)


class JobInconsistentStateError(JobRunException):
    def _log(self):
        logger.warning('%s: %s ' % (self.__class__.__name__, self.message))

    def __init__(self, status, expected, msg=''):
        message = 'Inconsistent job state, got "%s", expected: %s' % (status, expected)
        if msg != '':
            message = '%s ' % msg + message
        super(JobInconsistentStateError, self).__init__(message)


class JobPrepareException(JobRunException):
    """Preparation process errors"""
    pass


class JobRunException(JobRunException, Exception):
    """Run process errors"""
    pass