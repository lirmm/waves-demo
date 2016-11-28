""" Parse Bioblend connection errors """
from __future__ import unicode_literals

import json
from waves.adaptors.exceptions import AdaptorConnectException


class GalaxyAdaptorConnectionError(AdaptorConnectException):
    """
    Specific subclass for managing Galaxy service connection errors
    """
    def __init__(self, e):
        """
        Load and parse superclass ConnectionError message body
        :param e: The exception
        """

        class BaseError(Exception):
            def __init__(self, *args, **kwargs):
                super(BaseError, self).__init__(*args, **kwargs)

        if getattr(e, 'body'):
            error_data = json.loads(e.body)
        else:
            error_data = json.loads(e)
        message = '{}'.format(error_data['err_msg'])
        super(GalaxyAdaptorConnectionError, self).__init__(msg=message)
