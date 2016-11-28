""" WAVES Remote API calls base class """
from __future__ import unicode_literals

from ..base import JobRunnerAdaptor


class RemoteApiAdaptor(JobRunnerAdaptor):
    """ Base Class for remote API calls"""
    #: remote host url
    host = None
    #: remote host port
    port = None
    #: base remote api path
    api_base_path = ''
    #: remote endpoint
    api_endpoint = None

    # FIXME command seems to be mandatory..
    command = ""

    @property
    def init_params(self):
        return dict(host=self.host,
                    port=self.port,
                    api_base_path=self.api_base_path,
                    api_endpoint=self.api_endpoint)

    @property
    def complete_url(self):
        """ Create complete url string for remote api"""
        url = self.host
        if self.port:
            url += ':%s' % self.port
        if self.api_base_path:
            url += '/%s' % self.api_base_path
        if self.api_endpoint:
            url += '/%s' % self.api_endpoint
        return url
