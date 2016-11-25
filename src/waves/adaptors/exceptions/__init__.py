"""
Adaptor specific exceptions
"""
from __future__ import unicode_literals
import logging

__all__ = [str('AdaptorException'),
           str('AdaptorConnectException'),
           str('AdaptorExecException'),
           str('AdaptorJobException'),
           str('AdaptorInitError'),
           str('AdaptorNotReady')]


class AdaptorException(Exception):
    """ Base Adaptor exception class, should be raise upon specific Adaptor class exception catch
    this exception class is supposed to be catched
    """

    def __init__(self, base_exception=None, msg=''):
        if base_exception is not None:
            message = '[from:%s] - %s %s' % (base_exception.__class__.__name__,
                                             base_exception.message, msg)
            logging.getLogger('').exception(base_exception)
        else:
            message = msg
            logging.getLogger('').exception(msg)
        Exception.__init__(self, message)


class AdaptorConnectException(AdaptorException):
    """
    Adaptor Connection Error
    """
    pass


class AdaptorExecException(AdaptorException):
    """
    Adaptor execution error
    """
    pass


class AdaptorJobException(AdaptorException):
    """
    Adaptor JobRun Exception
    """
    pass


class AdaptorNotReady(Exception):
    """ Adaptor is not properly initialized to be used """

    def __init__(self):
        super(AdaptorNotReady, self).__init__('Adaptor is not ready')


class AdaptorInitError(AttributeError):
    """ Each adaptor expects some attributes for initialization, this exception should be raised when some mandatory
    parameters are missing
    """
    pass
