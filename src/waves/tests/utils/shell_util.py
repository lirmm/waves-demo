from __future__ import unicode_literals

import os
import unittest

from waves.tests.utils import get_sample_dir

NO_CLUSTER_MESSAGE = "A valid SGE cluster running is needed to run this tests"
MISSING_TOOL_MESSAGE = "Executable script is not in PATH : %s"


def skip_unless_sge():
    if not any(os.path.islink(os.path.join(_, 'qsub')) for _ in os.environ['PATH'].split(os.pathsep)):
        return unittest.skip(NO_CLUSTER_MESSAGE)
    return lambda f: f


def skip_unless_tool(program):
    """ Decorate a Cluster DRMAA test method as requiring a specific tool,
    skip the test case if the tool is unavailable (not in PATH).
    """
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    def method_wrapper(method):
        def wrapped_method(test, *args, **kwargs):
            found = False
            fpath, fname = os.path.split(program)
            if fpath:
                if is_exe(program) or is_exe(os.path.join(get_sample_dir(), program)):
                    found = True
            else:
                for path in os.environ["PATH"].split(os.pathsep):
                    path = path.strip('"')
                    exe_file = os.path.join(path, program)
                    # print "exe_file searched ", exe_file, is_exe(exe_file)
                    if is_exe(exe_file):
                        #print "found !!!!"
                        found = True
            # print "found ? ", found
            if not found:
                # print "not found"
                raise unittest.SkipTest(MISSING_TOOL_MESSAGE % program)

            return method(test, *args, **kwargs)

        # Must preserve method name so nose can detect and report tests by
        # name.
        wrapped_method.__name__ = method.__name__
        return wrapped_method

    return method_wrapper
