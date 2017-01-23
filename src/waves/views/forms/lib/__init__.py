from __future__ import unicode_literals

from multiupload.fields import MultiFileField
from django import forms
import waves.settings
import waves.const as const
from waves.models.inputs import *


class BaseHelper(object):

    def set_layout(self, service_input):
        raise NotImplementedError()

    def init_layout(self, fields):
        pass

    def end_layout(self):
        pass
