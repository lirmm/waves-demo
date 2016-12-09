from django.db import models


class SubmissionManager(models.Manager):
    """ Django object manager for submissions """

    def get_by_natural_key(self, api_name, service):
        """ Retrived Submission by natural key """
        return self.get(api_name=api_name, service=service)


class ServiceInputManager(models.Manager):
    def get_by_natural_key(self, label, name, default, service):
        return self.get(label=label, name=name, default=default, service=service)