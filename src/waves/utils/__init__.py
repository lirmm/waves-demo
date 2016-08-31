from __future__ import unicode_literals

import logging

__all__ = ['log_func_details', 'normalize_output', 'set_api_name']

logger = logging.getLogger(__name__)


def log_func_details(func):

    def decorate(*args, **kwargs):
        logger.info('---- %s', '.'.join([func.__module__, func.__name__]))
        # logger.debug('args: %s', args)
        # logger.debug('kwargs: %s', kwargs)
        returned = func(*args, **kwargs)
        logger.info('//-- end %s', '.'.join([func.__module__, func.__name__]))
        return returned
    return decorate


def normalize_output(value):
    import inflection
    import re
    value = re.sub(r'[^\w\.]+', '_', value)
    return inflection.underscore(value)


def set_api_name(value):
    return normalize_output(value)
