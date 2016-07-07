from __future__ import unicode_literals

import logging

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

import waves.const

logger = logging.getLogger(__name__)


class JobManager(models.Manager):
    def get_all_jobs(self):
        return self.all().values()

    def get_user_job(self, user):
        assert isinstance(user, get_user_model())
        try:
            admin_group = Group.objects.get(name=settings.WAVES_GROUP_ADMIN)
        except Group.DoesNotExist:
            admin_group = None
        if user.is_superuser or admin_group in user.groups.all():
            return self.all()
        return self.filter(Q(client=user) | Q(email_to=user.email))

    def get_pending_jobs(self, user=None):
        if user is not None:
            if user.is_super_user:
                # return all pending jobs
                return self.filter(status__in=(
                    waves.const.JOB_CREATED, waves.const.JOB_PREPARED, waves.const.JOB_QUEUED,
                    waves.const.JOB_RUNNING))
            # get only user jobs
            return self.filter(status__in=(waves.const.JOB_CREATED, waves.const.JOB_PREPARED,
                                           waves.const.JOB_QUEUED, waves.const.JOB_RUNNING),
                               client=user)
        # User is not supposed to be None
        return self.none()

    def get_created_job(self, extra_filter, user=None):
        if user is not None:
            self.filter(status=waves.const.JOB_CREATED,
                        client=user,
                        **extra_filter).order_by('-created')
        return self.filter(status=waves.const.JOB_CREATED, **extra_filter).order_by('-created').all()
