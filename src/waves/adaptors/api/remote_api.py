from __future__ import unicode_literals

from waves.adaptors.runner import JobRunnerAdaptor


class RemoteApiAdaptor(JobRunnerAdaptor):

    host = None
    port = None
    app_key = None
    api_base_path = None
    api_endpoint = None

    @property
    def init_params(self):
        return dict(host=self.host,
                    port=self.port,
                    api_base_path=self.api_base_path,
                    app_key=self.app_key,
                    api_endpoint=self.api_endpoint)
