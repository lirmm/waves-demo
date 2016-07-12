from __future__ import unicode_literals

import logging

from django.core.files.uploadedfile import TemporaryUploadedFile
from django.db import models, transaction
from django.core.exceptions import ObjectDoesNotExist

import waves.const
from waves.exceptions import *

logger = logging.getLogger(__name__)

__all__ = ['ServiceManager', 'WebSiteMetaMngr', 'DocumentationMetaMngr', 'DownloadLinkMetaMngr', 'FeatureMetaMngr',
           'MiscellaneousMetaMngr', 'CitationMetaMngr', 'CommandLineMetaMngr']


def _upload_job_file(in_input, job_input):
    if isinstance(in_input, TemporaryUploadedFile):
        filename = job_input.job.input_dir + in_input.name
        with open(filename, 'wb+') as uploaded_file:
            for chunk in in_input.chunks():
                uploaded_file.write(chunk)


class ServiceManager(models.Manager):
    def get_service_for_client(self, client):
        """

        Args:
            client:

        Returns:

        """
        return self.filter(authorized_clients__in=[client.pk], status__gte=waves.const.SRV_TEST)

    def get_public_services(self, user=None):
        """
        Returns:
        """
        if user is not None and (user.is_superuser or user.is_staff):
            return self.all()
        else:
            return self.filter(status=waves.const.SRV_PUBLIC)

    def _create_job_input(self, job, service_input, order, submitted_input):
        from waves.models import JobInput
        input_dict = dict(job=job,
                          name=service_input.name,
                          order=order,
                          type=service_input.type,
                          param_type=service_input.param_type,
                          related_service_input=service_input,
                          value=str(submitted_input))
        if service_input.type == waves.const.TYPE_FILE:
            assert isinstance(submitted_input, TemporaryUploadedFile), "Wrong data type for file %s" %service_input
            filename = job.input_dir + submitted_input.name
            with open(filename, 'wb+') as uploaded_file:
                for chunk in submitted_input.chunks():
                    uploaded_file.write(chunk)
        job.job_inputs.add(JobInput.objects.create(**input_dict))

    @transaction.atomic
    def create_new_job(self, service, email_to, submitted_inputs, user=None, title=None):
        """
        Create a new job from service data and submitted params values
        Args:
            title: Job title
            submitted_inputs: Dictionary { param_name:param_value }
            service: Service - related service
            email_to: email results to
            user: registered user (may be None)

        Returns:
            A newly created Job object
        """
        from waves.models import Job, JobInput, JobOutput
        job = Job.objects.create(service=service, email_to=email_to, client=user, title=title)
        order_inputs = 0
        try:
            for service_input in service.service_inputs.filter(editable=True, relatedinput=None):
                # Treat only non dependent inputs first
                order_inputs += 1
                incoming_input = submitted_inputs[service_input.name]
                # test service input mandatory, without default and no value
                if service_input.mandatory and not service_input.default and incoming_input is None \
                        and not hasattr(service_input, 'when_value'):
                    raise JobMissingMandatoryParam(service_input.name, job)
                # transform single incoming into list to keep process iso
                if type(incoming_input) != list:
                    incoming_input = [incoming_input]
                for in_input in incoming_input:
                    order_inputs += 1
                    self._create_job_input(job, service_input, order_inputs, in_input)
                    # TODO remove this kind of duplicated code
                    related_4_value = service_input.dependent_inputs.filter(when_value=str(in_input)).all()
                    for related_input in related_4_value:
                        income_input = submitted_inputs[related_input.name]
                        if type(income_input) != list:
                            income_input = [income_input]
                        for dep_input in income_input:
                            order_inputs += 1
                            self._create_job_input(job, related_input, order_inputs, dep_input)
        except KeyError:
            if service_input.mandatory and not service_input.default:
                raise JobMissingMandatoryParam(service_input.name, job=job)
            elif service_input.mandatory:
                job_input = JobInput.objects.create(
                    job=job,
                    name=service_input.name,
                    type=service_input.type,
                    value=service_input.default,
                    order=order_inputs
                )
                job.job_inputs.add(job_input)
            else:
                # parameters has not been submitted, but no mandatory
                pass
        except AssertionError as e:
            print e
            raise
            # raise JobSubmissionException('Unexpected error in job submission %s (%s)' % (service_input.get_type_display(), e), job=job)
        logger.debug('Job %s created with %i inputs', job.slug, job.job_inputs.count())
        for service_output in service.service_outputs.all():
            JobOutput.objects.create(job=job, name=service_output.name, label=service_output.name)
        return job

    def api_public(self):
        return self.filter(api_on=True, status=waves.const.SRV_PUBLIC)


class WebSiteMetaMngr(models.Manager):
    def get_queryset(self):
        return super(WebSiteMetaMngr, self).get_queryset().filter(type=waves.const.META_WEBSITE)


class DocumentationMetaMngr(models.Manager):
    def get_queryset(self):
        return super(DocumentationMetaMngr, self).get_queryset().filter(type=waves.const.META_DOC)


class DownloadLinkMetaMngr(models.Manager):
    def get_queryset(self):
        return super(DownloadLinkMetaMngr, self).get_queryset().filter(type=waves.const.META_DOWNLOAD)


class FeatureMetaMngr(models.Manager):
    def get_queryset(self):
        return super(FeatureMetaMngr, self).get_queryset().filter(type=waves.const.META_FEATURES)


class MiscellaneousMetaMngr(models.Manager):
    def get_queryset(self):
        return super(MiscellaneousMetaMngr, self).get_queryset().filter(type=waves.const.META_MISC)


class RelatedPaperMetaMngr(models.Manager):
    def get_queryset(self):
        return super(RelatedPaperMetaMngr, self).get_queryset().filter(type=waves.const.META_PAPER)


class CitationMetaMngr(models.Manager):
    def get_queryset(self):
        return super(CitationMetaMngr, self).get_queryset().filter(type=waves.const.META_CITE)


class CommandLineMetaMngr(models.Manager):
    def get_queryset(self):
        return super(DocumentationMetaMngr, self).get_queryset().filter(type=waves.const.META_CMD_LINE)
