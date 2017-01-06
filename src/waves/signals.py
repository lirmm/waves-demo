"""
WAVES Automated models signals handlers
"""
from __future__ import unicode_literals
import os
import logging
import shutil
import uuid
from os.path import join
from django.db.models.signals import pre_save, post_save, post_delete, pre_delete
from django.dispatch import receiver
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.contrib.auth.signals import user_logged_in
from ipware.ip import get_real_ip
from waves.models.base import ApiAble
from waves.models.jobs import Job, JobHistory, JobAdminHistory, JobOutput
from waves.models.services import *
from waves.models.submissions import *
from waves.models.runners import *
from waves.models.inputs import *
from waves.models.profiles import WavesProfile
from waves.utils.storage import profile_directory

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
        if instance.runner and (instance.has_changed_runner or instance.service_run_params.count() == 0):
            # create default service runner init params
            for param in instance.runner.runner_params.all():
                obj = ServiceRunParam.objects.create(service=instance, value=param.value, name=param.name,
                                                     prevent_override=param.prevent_override)
                instance.service_run_params.add(obj)


@receiver(pre_save, sender=Service)
def service_pre_save_handler(sender, instance, **kwargs):
    """ Pre save handler for Service model object, reset current Service Runner Init params if changed """
    if instance.has_changed_runner:
        # print "pre save "
        instance.service_run_params.all().delete()


@receiver(user_logged_in)
def login_action_handler(sender, user, **kwargs):
    """ Register user ip address upon login """
    request = kwargs.get('request')
    ip = get_real_ip(request)
    if ip is not None:
        logger.debug('Login action fired %s [%s]', user, ip)
        user_prof = user.profile
        user_prof.ip = ip
        user_prof.save(update_fields=['ip'])
    else:
        ip = request.META.get('REMOTE_ADDR', None)
        if ip is not None:
            logger.debug('Login action fired %s [%s]', user, ip)
            user_prof = user.profile
            user_prof.ip = ip
            user_prof.save(update_fields=['ip'])


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def profile_post_save_handler(sender, instance, created, **kwargs):
    """ Post save handler for Auth user model (create default WavesProfile if needed) """
    if created:
        # Create the profile object, only if it is newly created
        profile = WavesProfile(user=instance)
        profile.save()
    if instance.is_active and instance.profile.registered_for_api and not instance.profile.api_key:
        # User is activated, has registered for api services, and do not have any api_key
        instance.profile.api_key = uuid.uuid1()
        logger.debug("Update api_key for %s %s", instance, instance.profile.api_key)
    if instance.is_active and not instance.profile.registered_for_api:
        instance.profile.api_key = None
    instance.profile.save()


@receiver(post_delete, sender=WavesProfile)
def profile_post_delete_handler(sender, instance, **kwargs):
    """ Post delete handler for WavesProfile model objects """
    import shutil
    import os
    if os.path.exists(os.path.join(settings.MEDIA_ROOT, profile_directory(instance, ''))):
        shutil.rmtree(os.path.join(settings.MEDIA_ROOT, profile_directory(instance, '')))
    for usr_job in instance.clients_job.all():
        usr_job.delete()


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
            instance.runner_params.exclude(name__in=Adaptor().init_params.keys()).delete()
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


@receiver(pre_save, sender=ApiAble)
def api_able_pre_save_handler(sender, instance, **kwargs):
    """ Any ApiAble model object setup api_name if not already set in object data """
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


# Connect all ApiAble subclass to pre_save_handler
for subclass in ApiAble.__subclasses__():
    pre_save.connect(api_able_pre_save_handler, subclass)
