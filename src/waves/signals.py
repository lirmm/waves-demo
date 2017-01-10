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


@receiver(post_delete, sender=InputParam)
def service_input_post_delete_handler(sender, instance, **kwargs):
    """ SubmissionParam post delete handler"""
    if instance.input_samples.count() > 0:
        for sample in instance.input_samples.all():
            sample.file.delete()


@receiver(post_save, sender=Service)
def service_post_save_handler(sender, instance, created, **kwargs):
    """ Service post save handler"""
    if not kwargs.get('raw', False):
        if instance.runner and (instance.has_changed_runner or instance.srv_run_params.count() == 0):
            # create default service runner init params
            for param in instance.runner.runner_run_params.all():
                obj = ServiceRunParam.objects.create(service=instance, value=param.value, name=param.name,
                                                     prevent_override=param.prevent_override)
                instance.srv_run_params.add(obj)


@receiver(pre_save, sender=Service)
def service_pre_save_handler(sender, instance, **kwargs):
    """ Pre save handler for Service model object, reset current Service Runner Init params if changed """
    if instance.has_changed_runner:
        # print "pre save "
        instance.srv_run_params.all().delete()


@receiver(pre_save, sender=Runner)
def runner_pre_save_handler(sender, instance, **kwargs):
    if not kwargs.get('raw', False):
        if not instance.name and instance.clazz:
            instance.name = instance.clazz.rsplit('.', 1)[1]


@receiver(post_save, sender=Runner)
def runner_post_save_handler(sender, instance, created, **kwargs):
    """ Runner saved instance handler, setup or update related RunnerParam according to clazz specified """
    if not kwargs.get('raw', False):
        if created or instance.has_changed_clazz:
            # modified clazz instance.
            from django.utils.module_loading import import_string
            Adaptor = import_string(instance.clazz)
            # delete all old run params related to previous init_params from instance (delete cascade service params)
            instance.runner_run_params.exclude(name__in=Adaptor().init_params.keys()).delete()
            for name, initial in Adaptor().init_params.items():
                prevent_override = False
                if type(initial) == tuple:
                    initial = initial[0][0]
                    prevent_override = True
                RunnerParam.objects.update_or_create(defaults={'value': initial,
                                                               'prevent_override': prevent_override},
                                                     runner=instance,
                                                     name=name)
                for service in instance.runs.all():
                    service.reset_run_params()


@receiver(pre_save, sender=RunnerParam)
def runner_param_pre_save_handler(sender, instance, **kwargs):
    """ Runner param pre save handler """
    if instance.name.startswith('crypt_') and instance.value:
        from waves.utils.encrypt import Encrypt
        instance.value = Encrypt.encrypt(instance.value)


@receiver(post_save, sender=RunnerParam)
def runner_param_post_save_handler(sender, instance, created, **kwargs):
    """ Runner saved instance handler, setup or update related RunnerParam according to clazz specified """
    if instance.prevent_override:
        # Reset old upgrades values for related service to default
        for service_param in ServiceRunParam.objects.filter(name=instance.name):
            service_param._value = None
            service_param.save()


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
