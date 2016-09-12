from __future__ import unicode_literals

import logging
from django.contrib.sites.models import Site
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


def normalize_value(value):
    import inflection
    import re
    value = re.sub(r'[^\w\.]+', '_', value)
    return inflection.underscore(value)


def set_api_name(value):
    return normalize_value(value)


def get_complete_absolute_url(absolute_url):
    return 'http://%s%s' % (Site.objects.get_current().domain, absolute_url)
