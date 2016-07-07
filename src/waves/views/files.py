from __future__ import unicode_literals

import os

from django.views import generic
from django.http import HttpResponse
from django.utils.encoding import smart_str

from wsgiref.util import FileWrapper


class DownloadFileView(generic.DetailView):
    template_name = 'services/file.html'
    context_object_name = 'file'
    slug_field = 'slug'
    http_method_names = ['get', ]
    file_name = 'fake.txt'
    file_path = '/dev/null'

    def __init__(self, **kwargs):
        super(DownloadFileView, self).__init__(**kwargs)

    def render_to_response(self, context, **response_kwargs):
        """
            Creates a response with file asked, otherwise returns displayed file as 'Text'
            template response.
            """
        # Sniff if we need to return a CSV export
        if 'export' in self.request.GET:
            wrapper = FileWrapper(file(self.get_file_path()))
            response = HttpResponse(wrapper, content_type='application/force-download')
            response['Content-Disposition'] = 'attachment; filename="' + self.get_file_name() + '"'
            response['X-Sendfile'] = smart_str(self.get_file_path())
            response['Content-Length'] = os.path.getsize(self.get_file_path())
            return response
        else:
            return super(DownloadFileView, self).render_to_response(context, **response_kwargs)

    def get_file_name(self):
        return self.file_name

    def get_file_path(self):
        return self.file_path
