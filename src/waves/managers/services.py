from __future__ import unicode_literals

import logging
import os.path as path

from django.core.files.uploadedfile import TemporaryUploadedFile
from django.db import models, transaction
from django.core.exceptions import ObjectDoesNotExist
import waves.const
from waves.exceptions import *
from waves.models.samples import ServiceInputSample
from waves.utils import normalize

logger = logging.getLogger(__name__)

__all__ = ['ServiceManager', 'WebSiteMetaMngr', 'DocumentationMetaMngr', 'DownloadLinkMetaMngr', 'FeatureMetaMngr',
           'MiscellaneousMetaMngr', 'CitationMetaMngr', 'CommandLineMetaMngr']


class ServiceManager(models.Manager):
    def get_service_for_client(self, client):
        """

        Args:
            client:

        Returns:

        """
        return self.exclude(authorized_clients__in=[client.pk], status__lt=waves.const.SRV_TEST)

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
        try:
            if service_input.to_output:
                input_dict['value'] = normalize(input_dict['value'])
        except ObjectDoesNotExist:
            pass
        if service_input.type == waves.const.TYPE_FILE:
            if isinstance(submitted_input, TemporaryUploadedFile):
                # classic uploaded file
                filename = job.input_dir + submitted_input.name
                with open(filename, 'wb+') as uploaded_file:
                    for chunk in submitted_input.chunks():
                        uploaded_file.write(chunk)
            elif type(submitted_input) is int:
                # Manage sample data
                input_sample = ServiceInputSample.objects.get(pk=submitted_input)
                filename = job.input_dir + path.basename(input_sample.file.name)
                input_dict['value'] = path.basename(input_sample.file.name)
                with open(filename, 'wb+') as uploaded_file:
                    for chunk in input_sample.file.chunks():
                        uploaded_file.write(chunk)
            elif isinstance(submitted_input, basestring):
                # copy / paste content
                filename = job.input_dir + service_input.name + '.txt'
                input_dict.update(dict(value=service_input.name + '.txt'))
                with open(filename, 'wb+') as uploaded_file:
                    uploaded_file.write(submitted_input)
        job.job_inputs.add(JobInput.objects.create(**input_dict))

    @transaction.atomic
    def create_new_job(self, service, submitted_inputs, email_to=None, user=None):
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
        try:
            job_title = submitted_inputs.pop('title')
        except KeyError:
            job_title = ""
        job = Job.objects.create(service=service, email_to=email_to, client=user, title=job_title)
        order_inputs = 0
        try:
            for service_input in service.service_inputs.filter(editable=False):
                if service_input.name not in submitted_inputs:
                    # Update "submitted_inputs" dictionary with non editable ones with default value if not already set
                    submitted_inputs[service_input.name] = service_input.default
            for service_input in service.service_inputs.filter(editable=True, relatedinput=None):
                # Treat only non dependent inputs first
                order_inputs += 1
                incoming_input = submitted_inputs[service_input.name]
                # test service input mandatory, without default and no value
                if service_input.mandatory and not service_input.default and incoming_input is None \
                        and not hasattr(service_input, 'when_value'):
                    raise JobMissingMandatoryParam(service_input.name, job)
                if incoming_input:
                    # transform single incoming into list to keep process iso
                    if type(incoming_input) != list:
                        incoming_input = [incoming_input]
                    # TODO manage non editable fields, hidden fields in form ?
                    for in_input in incoming_input:
                        order_inputs += 1
                        self._create_job_input(job, service_input, order_inputs, in_input)
                        # TODO remove this kind of duplicated code
                        related_4_value = service_input.dependent_inputs.filter(when_value=str(in_input)).all()
                        for related_input in related_4_value:
                            income_input = submitted_inputs[related_input.name]
                            if income_input:
                                if type(income_input) != list:
                                    income_input = [income_input]
                                for dep_input in income_input:
                                    order_inputs += 1
                                    self._create_job_input(job, related_input, order_inputs, dep_input)
                                    # Manage 'non editable fields', add default values to inputs ?

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
            raise JobSubmissionException(
                'Unexpected error in job submission %s (%s)' % (service_input.get_type_display(), e), job=job)
        logger.debug('Job %s created with %i inputs', job.slug, job.job_inputs.count())
        for service_output in service.service_outputs.all():
            output_dict = dict(job=job, name=service_output.name, label=service_output.name, type=service_output.ext)
            if not service_output.from_input:
                JobOutput.objects.create(**output_dict)
            if service_output.from_input and submitted_inputs.get(service_output.from_input.name, None):
                # issued from a input value
                output_dict.update(dict(value=normalize(submitted_inputs.get(service_output.from_input.name,
                                                                             service_output.from_input.default)),
                                        may_be_empty=service_output.may_be_empty))
                JobOutput.objects.create(**output_dict)
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
