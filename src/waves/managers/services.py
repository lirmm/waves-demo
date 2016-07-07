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

    @staticmethod
    def import_submitted_input(incoming_input, service_input):
        input_dict = dict()
        if incoming_input is not None:
            logger.debug('Incoming %s ', incoming_input)
            if not service_input.multiple:
                if service_input.type == waves.const.TYPE_FILE:
                    # TYPE simple file
                    temp_file = incoming_input
                    # move temporary file to job input_dir
                    input_dict['value'] = temp_file.name
                elif service_input.type == waves.const.TYPE_LIST:
                    input_dict['value'] = incoming_input
                elif any(e == service_input.type for e, _ in waves.const.IN_TYPE[2:]):
                    # type boolean / list / integer / float / text
                    logger.info('Any ????')
                    input_dict['value'] = incoming_input
                else:
                    raise RuntimeError(
                        'Unexpected error in job submission %s ' % service_input.get_type_display())
                return input_dict
            else:
                input_dict = []
                for input_tmp in incoming_input:
                    input_dict.extend(ServiceManager.import_submitted_input(input_tmp, service_input))
                return input_dict

    @staticmethod
    @transaction.atomic
    def create_new_job(service, email_to, submitted_inputs, user=None, title=None):
        """Create a new job from service data and submitted params values
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
        job = Job.objects.create(service=service,
                                 email_to=email_to,
                                 client=user,
                                 title=title)
        job.make_job_dirs()
        order = 0
        for service_input in service.service_inputs.filter(relatedinput=None):
            try:
                order += 1
                incoming_input = submitted_inputs[service_input.name]
                input_dict = dict(job=job,
                                  name=service_input.name,
                                  order=order,
                                  type=service_input.type,
                                  param_type=service_input.param_type,
                                  related_service_input=service_input)
                # raise RuntimeError('Test Error')
                if service_input.mandatory and not service_input.default and incoming_input is None:
                    logger.info('Parameter submitted')
                    raise JobMissingMandatoryParam(service_input.name, job)
                details = ServiceManager.import_submitted_input(incoming_input, service_input)
                if service_input.dependent_inputs.count() > 0:
                    # import related data (and only this one)
                    try:
                        related_input_4_value = service_input.dependent_inputs.filter(
                            when_value=details['value']).first()
                        # TODO manage multiple 'when-value' ... ex with MAFTT
                        if related_input_4_value is not None:
                            logger.debug('Create dependent parameter %s ' % related_input_4_value)
                            order += 1
                            related_input_dict = dict(job=job,
                                                      name=related_input_4_value.name,
                                                      order=order,
                                                      type=related_input_4_value.type,
                                                      param_type=related_input_4_value.param_type)
                            related_input_dict.update(
                                ServiceManager.import_submitted_input(submitted_inputs[related_input_4_value.name],
                                                                      related_input_4_value))
                            related_input = JobInput.objects.create(**related_input_dict)
                            job.job_inputs.add(related_input)
                    except ObjectDoesNotExist as e:
                        logger.warn('Object does not exists')
                if service_input.type == waves.const.TYPE_FILE and isinstance(incoming_input, TemporaryUploadedFile):
                    logger.info('input name %s (upcoming %s)', service_input.name,
                                isinstance(incoming_input, TemporaryUploadedFile))
                    temp_file = incoming_input
                    filename = job.input_dir + temp_file.name
                    logger.debug('File job parameters:' + filename)
                    with open(filename, 'wb+') as uploaded_file:
                        for chunk in temp_file.chunks():
                            uploaded_file.write(chunk)
                if isinstance(details, dict):
                    input_dict.update(details)
                    job_input = JobInput.objects.create(**input_dict)
                    job.job_inputs.add(job_input)
                elif isinstance(details, list):
                    for input_data in details:
                        input_dict.update(input_data)
                    job_input = JobInput.objects.create(**input_dict)
                    job.job_inputs.add(job_input)
                elif incoming_input is not None:
                    raise JobCreateException('Valuated input could not be managed', job=job)
            except KeyError:
                if service_input.mandatory and not service_input.default:
                    raise JobMissingMandatoryParam(service_input.name, job=job)
                elif service_input.mandatory:
                    job_input = JobInput.objects.create(
                        job=job,
                        name=service_input.name,
                        type=service_input.type,
                        value=service_input.default,
                        order=order
                    )
                    job.job_inputs.add(job_input)
                else:
                    # parameters has not been submitted, but no mandatory
                    pass
            except AssertionError as e:
                raise JobCreateException('Unexpected error in job submission %s (%s)' %
                                         (service_input.get_type_display(), e.message), job=job)
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
