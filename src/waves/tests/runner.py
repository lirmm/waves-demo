from django.conf import settings


from django.test.runner import DiscoverRunner


class WavesTestRunner(DiscoverRunner):
    def __init__(self, pattern=None, top_level=None, verbosity=1, interactive=True, failfast=False, keepdb=False,
                 reverse=False, debug_sql=False, **kwargs):
        keepdb = getattr(settings, 'KEEP_TEST_DB', True)

        super(WavesTestRunner, self).__init__(pattern, top_level, verbosity, interactive, failfast, keepdb, reverse,
                                              debug_sql, **kwargs)

    def setup_test_environment(self, **kwargs):
        super(WavesTestRunner, self).setup_test_environment(**kwargs)
