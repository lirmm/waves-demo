""" Compphy server remote api adaptor"""
from __future__ import unicode_literals

import json
import pycurl
from StringIO import StringIO

import waves.const
from waves.adaptors.api.base import RemoteApiAdaptor
from waves.adaptors.exceptions import AdaptorJobException, AdaptorConnectException

__all__ = [str('CompPhyApiAdaptor')]

grp_name = "Remote API"


class CompPhyApiAdaptor(RemoteApiAdaptor):
    """
    CompPhy application remote api call to create CompPhy a new project
    """
    name = 'Compphy remote api adaptor'

    origin = None
    app_key = None

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
        """ CompPhy API adaptor init params dictionary """
        base = super(CompPhyApiAdaptor, self).init_params
        base.update(dict(origin=self.origin,
                         app_key=self.app_key))
        return base

    def _job_results(self, job):
        job.results_available = True
        return True

    def _prepare_job(self, job):
        # Nothing to do !
        pass

    def _cancel_job(self, job):
        # Unable to cancel !
        pass

    def _job_run_details(self, job):
        # Not JobDetails available
        pass

    def _run_job(self, job):
        try:
            curl = self._connector
            curl.setopt(pycurl.URL, self.host + self.api_base_path + self.api_endpoint)
            curl.setopt(pycurl.HTTPHEADER, ['Accept: application/json'])
            curl.setopt(pycurl.POST, 1)

            data = [("api_key", self.app_key), ("origin", self.origin), ("title", job.title)]
            for job_input_param in job.input_params.all():
                data.append((job_input_param.name, job_input_param.value))

            for job_input_file in job.input_files.all():
                file_full_path = job_input_file.file_path
                data.append((job_input_file.name, (pycurl.FORM_FILE, file_full_path)))

            curl.setopt(pycurl.HTTPPOST, data)

            buffer_curl = StringIO()

            curl.setopt(pycurl.WRITEFUNCTION, buffer_curl.write)
            curl.perform()

            status_code = curl.getinfo(pycurl.HTTP_CODE)
            curl.close()
            if status_code == 200:
                # TODO: Set id of the job
                res = json.loads(buffer_curl.getvalue())
                if res.get("success", False) is True:
                    job.remote_job_id = res.get("idProject", -1)
                    job.remote_history_id = res.get('access_key', '')
                    if job.remote_job_id == -1 or job.remote_history_id == '':
                        raise AdaptorJobException(None,
                                                  "An error has occurred. Please contact us to report the bug")
                else:
                    job.nb_retry = waves.settings.WAVES_JOBS_MAX_RETRY
                    raise AdaptorJobException(
                        res["message"] if "message" in res else "We are unable to launch your job. "
                                                                "Please contact us to report the bug"
                    )

            else:
                raise AdaptorJobException(
                    "Error while submitting project to CompPhy API. Please contact us to report the bug")
        except pycurl.error as e:
            raise AdaptorConnectException(e)

    def _job_status(self, job):
        try:
            curl = self._connector
            curl.setopt(pycurl.URL, self.host + self.api_base_path + self.api_endpoint + "/" + job.remote_job_id +
                        "?api_key=" + self.app_key + "&origin=" + self.origin + "&access_key=" +
                        job.remote_history_id)
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
                    if res.get("details", "") == "success":
                        output_url = job.job_outputs.filter(srv_output__isnull=False).first()
                        with open(output_url.file_path, 'w+') as fp:
                            fp.write(res['url'])
                    return res.get("details", "error")
                else:
                    raise AdaptorJobException(
                        BaseException("Error: status of job not found. Please contact us to report the bug."))
            else:
                raise AdaptorJobException(BaseException(
                    "Error: unable to contact CompPhy's API to get status. Please contact us to report the bug."))
        except pycurl.error as e:
            raise AdaptorConnectException(e)

    def _disconnect(self):
        self._connected = False
        self._connector = None

    def _connect(self):
        try:
            self._connected = True
            self._connector = pycurl.Curl()
        except pycurl.error as e:
            raise AdaptorConnectException(e)