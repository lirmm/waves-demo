from __future__ import unicode_literals

import logging
import os.path as path
from itertools import chain
from django.core.files.uploadedfile import TemporaryUploadedFile
from django.db import models, transaction
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

import waves.const
from waves.exceptions import *
from waves.models.samples import ServiceInputSample
from waves.models.jobs import JobInput, JobOutput
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
                          order=order,
                          srv_input=service_input,
                          value=str(submitted_input))
        try:
            if service_input.to_output.exists():
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
                        # input_dict.update(dict(value='inputs/' + submitted_input.name))
            elif type(submitted_input) is int:
                # Manage sample data
                input_sample = ServiceInputSample.objects.get(pk=submitted_input)
                filename = job.input_dir + path.basename(input_sample.file.name)
                input_dict['value'] = path.basename(input_sample.file.name)
                with open(filename, 'wb+') as uploaded_file:
                    for chunk in input_sample.file.chunks():
                        uploaded_file.write(chunk)
                        # input_dict.update(dict(value='inputs/' + submitted_input.name))
            elif isinstance(submitted_input, basestring):
                # copy / paste content
                filename = job.input_dir + service_input.name + '.txt'
                input_dict.update(dict(value=service_input.name + '.txt'))
                with open(filename, 'wb+') as uploaded_file:
                    uploaded_file.write(submitted_input)
        job.job_inputs.add(JobInput.objects.create(**input_dict))

    def _check_mandatory_inputs(self, service, inputs):
        """
        Check presence for mandatory job creation inputs
        Args:
            inputs:

        Returns:
            None
        Raises:
            ValidationException

        """
        from waves.models import RelatedInput
        inputs = service.service_inputs.filter(mandatory=True, editable=True, default="")
        related_inputs = RelatedInput.objects.filter(mandatory=True, related_to__service=service)
        for field in list(chain(*[inputs, related_inputs])):
            print field
            # raise JobMissingMandatoryParam(service_input.name, job)
            jobInput = JobInput()
            # retrieve validator for input
            # validator = field.validator()
            field.clean()
            pass

    def _check_service_inputs(self, inputs):
        """
        Apply validation on all inputs, according to related service input
        Args:
            inputs:

        Returns:
            None
        Raises:
            ValidationException

        """

    @transaction.atomic
    def create_new_job(self, service, submitted_inputs, email_to=None, user=None):
        """
        Create a new job from service data and submitted params values
        Args:
            submitted_inputs: Dictionary { param_name:param_value }
            service: Service - related service
            email_to: email results to
            user: associated user (may be None)
        Returns:
            A newly created Job object
        """
        from waves.models import Job, JobInput, BaseInput, JobOutput, RelatedInput
        try:
            job_title = submitted_inputs.pop('title')
        except KeyError:
            job_title = ""
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug('Received data :')
        for key in submitted_inputs:
            logger.debug('Param %s: %s', key, submitted_inputs[key])
        # self._check_mandatory_inputs(service, submitted_inputs)
        job = Job.objects.create(service=service, email_to=email_to, client=user, title=job_title)
        # First create inputs
        all_inputs = BaseInput.objects.filter(
            (Q(name__in=submitted_inputs.keys()) | Q(mandatory=True)), editable=True, service=service)
        # print all_inputs
        # print submitted_inputs
        for service_input in all_inputs: #list(chain(*[inputs, related_inputs])):
            # Treat only non dependent inputs first
            incoming_input = submitted_inputs.get(service_input.name, None)
            logger.debug("current Service Input: %s, %s, %s", service_input, service_input.mandatory, incoming_input)
            # test service input mandatory, without default and no value
            if service_input.mandatory and not service_input.default and incoming_input is None:
                raise JobMissingMandatoryParam(service_input.label, job)
            if incoming_input:
                logger.debug('Retrieved "%s" for service input "%s:%s"', incoming_input, service_input.label,
                             service_input.name)
                # transform single incoming into list to keep process iso
                if type(incoming_input) != list:
                    incoming_input = [incoming_input]
                for in_input in incoming_input:
                    self._create_job_input(job, service_input, service_input.order, in_input)
        # create expected outputs
        for service_output in service.service_outputs.all():
            output_dict = dict(job=job, srv_output=service_output)
            if not service_output.from_input:
                job.job_outputs.add(JobOutput.objects.create(**output_dict))
            else:
                # issued from a input value
                output_dict.update(dict(value=normalize(submitted_inputs.get(service_output.from_input.name,
                                                                             service_output.from_input.default)),
                                        may_be_empty=service_output.may_be_empty))
                job.job_outputs.add(JobOutput.objects.create(**output_dict))
        logger.debug('Job %s created with %i inputs', job.slug, job.job_inputs.count())
        if logger.isEnabledFor(logging.DEBUG):
            # LOG full command line
            logger.debug('Job %s command will be :', job.title)
            logger.debug('%s', job.command_line)
            logger.debug('Expected outputs will be:')
            for j_output in job.job_outputs.all():
                logger.debug('Output %s: %s (maybe_empty: %s)', j_output.name, j_output.value,
                             j_output.may_be_empty)

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
