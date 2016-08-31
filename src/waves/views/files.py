from __future__ import unicode_literals

import os

from django.views import generic
from django.http import HttpResponse
from django.utils.encoding import smart_str
from django.http import Http404

from wsgiref.util import FileWrapper


class DownloadFileView(generic.DetailView):
    template_name = 'services/file.html'
    context_object_name = 'file'
    slug_field = 'slug'
    http_method_names = ['get', ]

    def __init__(self, **kwargs):
        super(DownloadFileView, self).__init__(**kwargs)

    def get_object(self, queryset=None):
        object = super(DownloadFileView, self).get_object(queryset)
        if not os.path.isfile(object.file_path):
            raise Http404('File does not exists')
        return object

    def render_to_response(self, context, **response_kwargs):
        """
            Creates a response with file asked, otherwise returns displayed file as 'Text'
            template response.
        """
        # Sniff if we need to return a CSV export
        if 'export' in self.request.GET:
            wrapper = FileWrapper(file(self.file_path))
            response = HttpResponse(wrapper, content_type='application/force-download')
            response['Content-Disposition'] = 'attachment; filename="' + self.file_name + '"'
            response['X-Sendfile'] = smart_str(self.file_path)
            response['Content-Length'] = os.path.getsize(self.file_path)
            return response
        else:
            return super(DownloadFileView, self).render_to_response(context, **response_kwargs)

    def get_context_data(self, **kwargs):
        context = super(DownloadFileView, self).get_context_data(**kwargs)
        if 'export' not in self.request.GET:
            with open(self.file_path) as fp:
                context['file_content'] = fp.read()
            context['return_link'] = self.return_link
            context['file_description'] = self.file_description
            context['file_name'] = self.file_name
        return context

    @property
    def return_link(self):
        return "#"

    @property
    def file_description(self):
        raise NotImplementedError('file_description function must be defined')

    @property
    def file_name(self):
        raise NotImplementedError('file_name function must be defined')

    @property
    def file_path(self):
        raise NotImplementedError('file_path function must be defined')
