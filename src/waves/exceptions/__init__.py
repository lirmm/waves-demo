# -*- coding: utf-8 -*-
# TODO move exceptions classes into dedicated files
from __future__ import unicode_literals

import logging
import sys

__all__ = ['WavesException', 'RunnerException', 'RunnerNotInitialized', 'RunnerNotReady', 'RunnerConnectionError',
           'JobException', 'JobInconsistentStateError', 'JobMissingMandatoryParam', 'JobPrepareException',
           'JobRunException', 'JobSubmissionException', 'JobCreateException', 'RunnerUnexpectedInitParam']
if sys.version_info[0] < 3:
    __all__ = [n.encode('ascii') for n in __all__]
logger = logging.getLogger(__name__)


class WavesException(Exception):
    """
    Waves base exception class, add log corresponding logger
    """
    def _log(self):
        logger.fatal('%s: %s ' % (self.__class__.__name__, self.message), exc_info=sys.exc_info())

    def __init__(self, *args, **kwargs):
        super(WavesException, self).__init__(*args, **kwargs)
        # TODO find new cool method to print stack trace related to THIS exception
        # self._log()


class RunnerException(WavesException):
    """
    Base Exception class for all Runner related errors
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
        super(JobException, self).__init__(message)


class JobRunException(JobException):
    """More specifically related job run errors"""
    pass


class JobSubmissionException(JobException):
    """More specifically related job preparation errors"""
    pass


class JobCreateException(JobSubmissionException):
    def __init__(self, message, job=None):
        super(JobException, self).__init__(message)
        if job is not None:
            job.delete()


class JobMissingMandatoryParam(JobSubmissionException):
    def __init__(self, param, job):
        message = u'Missing mandatory parameter "%s"' % param
        super(JobMissingMandatoryParam, self).__init__(message, job)


class JobInconsistentStateError(JobRunException):
    def _log(self):
        logger.warning('%s: %s ' % (self.__class__.__name__, self.message))

    def __init__(self, status, expected, msg=''):
        message = u'Inconsistent job state, got "%s", expected: %s' % (status, expected)
        if msg != '':
            message = '%s ' % msg + message
        super(JobInconsistentStateError, self).__init__(message)


class JobPrepareException(JobRunException):
    """Preparation process errors"""
    pass
