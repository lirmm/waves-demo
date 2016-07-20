from __future__ import unicode_literals

import logging
import inspect

__all__ = ['log_func_details']

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


def service_sample_directory(instance, filename):
    return 'sample/{0}/{1}'.format(instance.service.api_name, filename)


def normalize(value):
    import inflection
    import re
    temp_name = re.sub(r'\W+', '_', value)
    return inflection.underscore(temp_name)


def set_api_name(value):
    return normalize(value)
