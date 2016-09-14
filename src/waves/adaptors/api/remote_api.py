from __future__ import unicode_literals

from waves.adaptors.runner import JobRunnerAdaptor


class RemoteApiAdaptor(JobRunnerAdaptor):

    host = None
    port = None
    app_key = None
    url_path = None

    @property
    def init_params(self):
        return dict(host=self.host,
                    port=self.port,
                    app_key=self.app_key,
                    url_path=self.url_path)
