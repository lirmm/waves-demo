"""
A copy of bioblend libraty unit tests decorators, with added few functionality
Based on https://github.com/galaxyproject/bioblend/
Author : Marc Chakiachvili
"""
import unittest
import bioblend
from bioblend.galaxy.client import ConnectionError
import waves.settings


NO_GALAXY_MESSAGE = "Externally configured Galaxy, but connection failed. %s"
WRONG_GALAXY_KEY = "A Galaxy server is running, but provided waves_api key is wrong."
MISSING_SETTINGS = "Some settings are required to run Galaxy test : WAVES_TEST_GALAXY_URL, WAVES_TEST_GALAXY_PORT, " \
                   "WAVES_TEST_GALAXY_API_KEY."
MISSING_TOOL_MESSAGE = "Externally configured Galaxy instance requires tool %s to run test."
MISSING_GALAXY_ADDON = 'Galaxy api adaptor addon missing'


def skip_unless_galaxy():
    try:
        __import__('waves_addons.adaptors.api.galaxy')
        from waves_addons.adaptors.api.galaxy import GalaxyJobAdaptor, GalaxyWorkFlowAdaptor
        galaxy_key = waves.settings.WAVES_TEST_GALAXY_API_KEY
        galaxy_url = waves.settings.WAVES_TEST_GALAXY_URL
        if waves.settings.WAVES_TEST_GALAXY_PORT:
            galaxy_url += ':%s' % waves.settings.WAVES_TEST_GALAXY_PORT
        gi = bioblend.galaxy.GalaxyInstance(url=galaxy_url, key=galaxy_key)
        bioblend.galaxy.users.UserClient(gi).get_current_user()
    except ConnectionError as e:
        return unittest.skip(NO_GALAXY_MESSAGE % e + ' [' + galaxy_url + '][' + galaxy_key + ']')
    except AttributeError:
        return unittest.skip(MISSING_SETTINGS)
    except ImportError:
        return unittest.skip(MISSING_GALAXY_ADDON)
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
