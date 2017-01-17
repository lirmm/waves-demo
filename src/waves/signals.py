"""
WAVES Automated models signals handlers
"""
from __future__ import unicode_literals

import logging
import os
import shutil
from os.path import join

from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver

from waves.models.base import ApiModel
from waves.models.adaptors import AdaptorInitParam, HasRunnerAdaptorParamsMixin
from waves.models.inputs import *
from waves.models.jobs import Job, JobOutput
from waves.models.runners import *
from waves.models.services import *
from waves.models.submissions import *

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Job)
def job_pre_save_handler(sender, instance, **kwargs):
    """ job presave handler """
    if not instance.title:
        instance.title = '%s_%s' % (instance.service.api_name, instance.slug)


@receiver(post_save, sender=Job)
def job_post_save_handler(sender, instance, created, **kwargs):
    """ job post save handler """
    if not kwargs.get('raw', False):
        if created:
            instance.save_status(instance.status)
            # create job working dirs locally
            instance.make_job_dirs()
            # initiate default outputs
            instance.create_default_outputs()
        elif instance.changed_status:
            instance.save_status(instance.status)


@receiver(post_delete, sender=Job)
def job_post_delete_handler(sender, instance, **kwargs):
    """ post delete job handler """
    instance.delete_job_dirs()


@receiver(post_delete, sender=Service)
def service_post_delete_handler(sender, instance, **kwargs):
    """ service post delete handler """
    if os.path.exists(instance.sample_dir):
        shutil.rmtree(instance.sample_dir)


@receiver(pre_save, sender=Submission)
def submission_pre_save_handler(sender, instance, **kwargs):
    """ submission pre save """
    if not instance.label:
        instance.label = instance.service.name


@receiver(post_save, sender=Submission)
def submission_pre_save_handler(sender, instance, created, **kwargs):
    """ submission pre save """
    if created and not kwargs.get('raw', False):
        instance.exit_codes.add(SubmissionExitCode.objects.create(submission=instance, exit_code=0,
                                                                  message='Process exit normally'))
        instance.exit_codes.add(SubmissionExitCode.objects.create(submission=instance, exit_code=1,
                                                                  message='Process exit error'))


@receiver(post_delete, sender=FileInputSample)
def service_sample_post_delete_handler(sender, instance, **kwargs):
    """ SubmissionSample delete handler """
    if instance.file:
        instance.file.delete()


@receiver(post_delete, sender=FileInput)
def service_input_post_delete_handler(sender, instance, **kwargs):
    """ SubmissionParam post delete handler"""
    if instance.input_samples.count() > 0:
        for sample in instance.input_samples.all():
            sample.file.delete()


@receiver(pre_save, sender=Runner)
def runner_pre_save_handler(sender, instance, **kwargs):
    if not kwargs.get('raw', False):
        if not instance.name and instance.clazz:
            instance.name = instance.clazz.rsplit('.', 1)[1]


@receiver(post_save, sender=HasRunnerAdaptorParamsMixin)
def has_runner_post_save_handler(sender, instance, created, **kwargs):
    if instance.has_changed_runner and not kwargs.get('raw', False):
        print "in signal"
        from django.utils.module_loading import import_string
        from django.contrib.contenttypes.models import ContentType
        object_ctype = ContentType.objects.get_for_model(instance)
        Adaptor = import_string(instance.get_clazz())
        instance.adaptor_params.exclude(name__in=Adaptor().init_params.keys()).delete()
        # delete all old run params related to previous init_params from instance (delete cascade service params)
        for name, initial in Adaptor().init_params.items():

            prevent_override = False
            if type(initial) in (tuple, list, dict):
                initial = initial[0][0]
                prevent_override = True
            AdaptorInitParam.objects.update_or_create(defaults={'value': initial,
                                                                'prevent_override': prevent_override},
                                                      content_type=object_ctype, object_id=instance.pk,
                                                      name=name)

for subclass in HasRunnerAdaptorParamsMixin.__subclasses__():
    post_save.connect(has_runner_post_save_handler, subclass)


@receiver(post_save, sender=Runner)
def runner_post_save_handler(sender, instance, created, **kwargs):
    """ Runner saved instance handler, setup or update related RunnerInitParam according to clazz specified """
    if not kwargs.get('raw', False):
        if created or instance.has_changed_runner:
            # modified clazz instance.
            for service in instance.runs.all():
                service.reset_run_params()


@receiver(pre_save, sender=AdaptorInitParam)
def adaptor_param_pre_save_handler(sender, instance, **kwargs):
    """ Runner param pre save handler """
    if instance.name.startswith('crypt_') and instance.value:
        from waves.utils.encrypt import Encrypt
        instance.value = Encrypt.encrypt(instance.value)

"""
@receiver(post_save, sender=AdaptorInitParam)
def adaptor_param_post_save_handler(sender, instance, created, **kwargs):
    "" Runner saved instance handler, setup or update related RunnerInitParam according to clazz specified ""
    if instance.prevent_override:
        from django.contrib.contenttypes.models import ContentType

        # Reset old upgrades values for related service to default
        object_ctype = ContentType.objects.get_for_model(sender.__class__.__name__)
        for service_param in AdaptorInitParam.objects.filter(name=instance.name, object_ctype=object_ctype):
            service_param.value = instance.value
            service_param.save()
"""

@receiver(pre_save, sender=ApiModel)
def api_able_pre_save_handler(sender, instance, **kwargs):
    """ Any ApiModel model object setup api_name if not already set in object data """
    if not instance.api_name or instance.api_name == '':
        instance.api_name = instance.create_api_name()
        exists = instance.duplicate_api_name()
        if exists.count() > 0:
            instance.api_name += '_' + str(exists.count())


@receiver(post_save, sender=JobOutput)
def job_output_post_save_handler(sender, instance, created, **kwargs):
    """ Job Output post save handler """
    if created and instance.value and not kwargs.get('raw', False):
        # Create empty file for expected outputs
        open(join(instance.job.working_dir, instance.value), 'a').close()


# Connect all ApiModel subclass to pre_save_handler
for subclass in ApiModel.__subclasses__():
    pre_save.connect(api_able_pre_save_handler, subclass)


