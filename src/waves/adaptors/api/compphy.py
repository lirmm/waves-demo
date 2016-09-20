from __future__ import unicode_literals

from remote_api import RemoteApiAdaptor

from waves.exceptions import JobRunException
import waves.settings, waves.const
import pycurl, os, json
from StringIO import StringIO


class CompPhyApiAdaptor(RemoteApiAdaptor):

    origin = None

    def __init__(self, **kwargs):
        super(CompPhyApiAdaptor, self).__init__(**kwargs)
        self._states_map = dict(
            creating=waves.const.JOB_RUNNING,
            success=waves.const.JOB_COMPLETED,
            error=waves.const.JOB_ERROR,
            warning=waves.const.JOB_COMPLETED
        )

    @property
    def init_params(self):
        base = super(CompPhyApiAdaptor, self).init_params
        base.update(dict(origin=self.origin))
        return base

    def _job_results(self, job):
        return True

    def _prepare_job(self, job):
        pass

    def _cancel_job(self, job):
        pass

    def _job_run_details(self, job):
        pass

    def _run_job(self, job):
        curl = self._connector
        curl.setopt(pycurl.URL, self.host + self.api_base_path + self.api_endpoint)
        curl.setopt(pycurl.HTTPHEADER, ['Accept: application/json'])
        curl.setopt(pycurl.POST, 1)

        data = [("api_key", self.app_key), ("origin", self.origin), ("title", job.title)]
        for job_input_param in job.input_params.all():
            data.append((job_input_param.name, job_input_param.value))

        for job_input_file in job.input_files.all():
            file_full_path = job_input_file.file_path
            data.append((job_input_file.srv_input.name, (pycurl.FORM_FILE, file_full_path)))

        curl.setopt(pycurl.HTTPPOST, data)

        buffer_curl = StringIO()

        curl.setopt(pycurl.WRITEFUNCTION, buffer_curl.write)
        curl.perform()

        status_code = curl.getinfo(pycurl.HTTP_CODE)
        curl.close()
        if status_code == 200:
            # TODO: Set id of the job
            res = json.loads(buffer_curl.getvalue())
            if res["success"]:
                job.remote_job_id = res["idProject"]
                job.eav.compphy_remote_access_key = res['access_key']
            else:
                job.nb_retry = waves.settings.WAVES_JOBS_MAX_RETRY
                raise JobRunException(
                    res["message"] if "message" in res else "An error has occurred. Please contact us to report the bug"
                )

        else:
            raise JobRunException(
                "Error while submitting project to CompPhy API. Please contact us to report the bug")
        job.save()

    def _job_status(self, job):
        curl = self._connector
        curl.setopt(pycurl.URL, self.host + self.api_base_path + self.api_endpoint + "/" + job.remote_job_id +
                    "?api_key=" + self.app_key + "&origin=" + self.origin + "&access_key=" +
                    job.eav.compphy_remote_access_key)
        curl.setopt(pycurl.HTTPHEADER, ['Accept: application/json'])
        curl.setopt(pycurl.HTTPGET, 1)
        curl.setopt(pycurl.POST, 0)
        buffer_curl = StringIO()

        curl.setopt(pycurl.WRITEFUNCTION, buffer_curl.write)
        curl.perform()

        status_code = curl.getinfo(pycurl.HTTP_CODE)
        curl.close()
        if status_code == 200:
            res = json.loads(buffer_curl.getvalue())
            if "status" in res:
                if res["details"] == "success":
                    output_url = job.job_outputs.filter(srv_output__isnull=False).first()
                    with open(output_url.file_path, 'w+') as fp:
                        fp.write(res['url'])
                return res["details"]
            else:
                raise JobRunException("Error: status of job not found. Please contact us to report the bug.")
        else:
            raise JobRunException("Error: unable to contact CompPhy's API to get status. Please contact us to report the bug.")

    def _disconnect(self):
        pass

    def _connect(self):
        self._connected = True
        self._connector = pycurl.Curl()
        pass