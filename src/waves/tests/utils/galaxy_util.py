"""
A copy of bioblend libraty unit tests decorators, with added few functionality
Based on https://github.com/galaxyproject/bioblend/
Author : Marc Chakiachvili
"""
import unittest
import bioblend
from bioblend.galaxy.client import ConnectionError

from django.conf import settings


NO_GALAXY_MESSAGE = "Externally configured Galaxy, but connection failed."
WRONG_GALAXY_KEY = "A Galaxy server is running, but provided api key is wrong."
MISSING_SETTINGS = "Some settings are required to run Galaxy test : WAVES_GALAXY_URL, WAVES_GALAXY_PORT, " \
                   "WAVES_GALAXY_KEY."
MISSING_TOOL_MESSAGE = "Externally configured Galaxy instance requires tool %s to run test."


def skip_unless_galaxy():
    try:
        galaxy_key = settings.WAVES_GALAXY_API_KEY
        galaxy_url = '%s:%s' % (settings.WAVES_GALAXY_URL, settings.WAVES_GALAXY_PORT)
        gi = bioblend.galaxy.GalaxyInstance(url=galaxy_url, key=galaxy_key)
        bioblend.galaxy.users.UserClient(gi).get_current_user()
    except ConnectionError:
        return unittest.skip(NO_GALAXY_MESSAGE + ' [' + galaxy_url + '][' + galaxy_key + ']')
    except AttributeError:
        return unittest.skip(MISSING_SETTINGS)
    return lambda f: f


def skip_unless_tool(tool_id):
    """ Decorate a Galaxy test method as requiring a specific tool,
    skip the test case if the tool is unavailable.
    """

    def method_wrapper(method):
        def wrapped_method(has_gi, *args, **kwargs):
            tools = has_gi.gi.tools.list()
            # In panels by default, so flatten out sections...
            tool_ids = [_.id for _ in tools]
            tool_names = [_.name for _ in tools]
            if tool_id not in tool_ids and not tool_id not in tool_names:
                raise unittest.SkipTest(MISSING_TOOL_MESSAGE % tool_id)

            return method(has_gi, *args, **kwargs)

        # Must preserve method name so nose can detect and report tests by
        # name.
        wrapped_method.__name__ = method.__name__
        return wrapped_method

    return method_wrapper
