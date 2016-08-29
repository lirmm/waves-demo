from __future__ import unicode_literals

import waves.settings


def assertion_tracker(func):

    def method_wrapper(method):
        def wrapped_method(test, *args, **kwargs):
            return method(test, *args, **kwargs)

        # Must preserve method name so nose can detect and report tests by
        # name.
        wrapped_method.__name__ = method.__name__
        return wrapped_method

    return method_wrapper


def get_sample_dir():
    return waves.settings.WAVES_DATA_ROOT
