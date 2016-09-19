from __future__ import unicode_literals

from remote_api import RemoteApiAdaptor

from waves.exceptions import JobPrepareException

import pycurl, os, json
from StringIO import StringIO


class CompPhyApiAdaptor(RemoteApiAdaptor):

    def _job_results(self, job):
        pass

    def _prepare_job(self, job):
        curl = self._connector
        curl.setopt(pycurl.URL, self.host + self.api_base_path + self.api_endpoint)
        curl.setopt(pycurl.HTTPHEADER, ['Accept: application/json'])
        curl.setopt(pycurl.POST, 1)

        # Get files:
        #job.input_params.get(srv_input__name='title')

        data = {"apiKey": self.app_key}
        for job_input_param in job.input_params.all():
            data[job_input_param.name] = job_input_param.value

        curl.setopt(pycurl.POSTFIELDS, json.dumps(data))

        uploaded_files = []
        for job_input_file in job.input_files.all():
            file_full_path = os.path.join(job.input_dir, job_input_file.value)
            uploaded_files.append((job_input_file.value, (pycurl.FORM_FILE, file_full_path)))

        curl.setopt(pycurl.HTTPPOST, uploaded_files)

        buffer_curl = StringIO()

        curl.setopt(pycurl.WRITEFUNCTION, buffer_curl.write)
        curl.perform()
        curl.close()

        status_code = curl.getinfo(pycurl.HTTP_CODE)
        if status_code == 200:
            # TODO: Set id of the job
            res = json.loads(buffer_curl.getvalue())
        else:
            raise JobPrepareException("Error while submitting project to CompPhy API. Please contact us to report the bug")

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
        self._connector = pycurl.Curl()
        pass