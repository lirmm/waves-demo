""" Base class for exporting objects """
from __future__ import unicode_literals

from waves.views.files import DownloadFileView
from django.http import Http404
from django.shortcuts import redirect
from waves.models.base import ExportAbleMixin
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib import messages
import json
import waves.settings
from os.path import join
import logging
logger = logging.getLogger(__name__)


class ModelExportView(DownloadFileView):
    """ Enable simple model export with DRF subclasses must declare property method to set up
    serializer used for process
    """
    model = None
    _force_download = True
    serializer = None
    return_view = "admin:index"

    def get_context_data(self, **kwargs):
        assert isinstance(self.object, ExportAbleMixin), 'Model object must be Export-able'
        self.object.serialize()
        context = super(ModelExportView, self).get_context_data(**kwargs)
        return context

    def get(self, request, *args, **kwargs):
        from waves.models.base import ExportError
        try:
            return super(ModelExportView, self).get(request, *args, **kwargs)
        except ExportError as e:
            messages.error(self.request, 'Oups: %s' % e)
            return redirect(self.return_view)

    @property
    def file_path(self):
        return join(waves.settings.WAVES_DATA_ROOT, self.file_name)

    @property
    def file_name(self):
        return self.object.export_file_name

    @property
    def file_description(self):
        return "Export file for %s " % self.model.__class__.__name__

