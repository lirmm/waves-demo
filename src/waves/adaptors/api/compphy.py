from __future__ import unicode_literals

from remote_api import RemoteApiAdaptor


class CompPhyApiAdaptor(RemoteApiAdaptor):


    def _job_results(self, job):
        pass

    def _prepare_job(self, job):
        pass

    def _cancel_job(self, job):
        pass

    def _job_run_details(self, job):
        pass

    def _run_job(self, job):
        pass

    def _job_status(self, job):
        pass

    def _disconnect(self):
        pass

    def _connect(self):
        self.connected = True
        # self._connector = pycurl.Curl()
        pass