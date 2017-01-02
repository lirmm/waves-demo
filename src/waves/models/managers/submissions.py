""" Submissions Models Managers """
from __future__ import unicode_literals

from django.db import models
import waves.const

__all__ = ['SubmissionManager', 'SubmissionInputManager', 'FileInputManager', 'ParamManager', 'RelatedParamManager',
           'RelatedFileManager', 'SubmissionRunParamManager']


class SubmissionManager(models.Manager):
    """ Django object manager for submissions """

    def get_by_natural_key(self, api_name, service):
        """ Retrived Submission by natural key """
        return self.get(api_name=api_name, service=service)


class SubmissionInputManager(models.Manager):
    def get_by_natural_key(self, label, name, default, service):
        return self.get(label=label, name=name, default=default, service=service)


class FileInputManager(models.Manager):
    def get_queryset(self):
        return super(FileInputManager, self).get_queryset().filter(type=waves.const.TYPE_FILE,
                                                                   related_to__isnull=True)


class ParamManager(models.Manager):
    def get_queryset(self):
        return super(ParamManager, self).get_queryset().exclude(type=waves.const.TYPE_FILE).filter(
            related_to__isnull=True)


class RelatedParamManager(models.Manager):
    def get_queryset(self):
        return super(RelatedParamManager, self).get_queryset().exclude(type=waves.const.TYPE_FILE).filter(
            related_to__isnull=False)


class RelatedFileManager(models.Manager):
    def get_queryset(self):
        return super(RelatedFileManager, self).get_queryset().filter(type=waves.const.TYPE_FILE,
                                                                     related_to__isnull=False)


class SubmissionRunParamManager(models.Manager):
    def get_queryset(self):
        return super(SubmissionRunParamManager, self).get_queryset().filter(prevent_override=False)
