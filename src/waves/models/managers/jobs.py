""" Jobs Managers class """
from __future__ import unicode_literals

import waves.adaptors.const
import waves.adaptors.const as jobconst
from django.db import models
from django.db.models import Q

from waves.models.submissions import SubmissionOutput

__all__ = ['JobAdminHistoryManager', 'JobHistoryManager', "JobInputManager", "JobManager", "JobOutputManager"]


class JobManager(models.Manager):
    """ Job Manager add few shortcut function to default Django models objects Manager
    """

    def get_by_natural_key(self, slug, service):
        return self.get(slug=slug, service=service)

    def get_all_jobs(self):
        """
        Return all jobs currently registered in database, as list of dictionary elements
        :return: QuerySet
        """
        return self.all().values()

    def get_user_job(self, user):
        """
        Filter jobs according to user (logged in) according to following access rule:
        * User is a super_user, return all jobs
        * User is member of staff (access to Django admin): returns only jobs from services user has created,
        jobs created by user, or where associated email is its email
        * User is simply registered on website, returns only those created by its own
        :param user: current user (may be Anonymous)
        :return: QuerySet
        """
        if user.is_superuser:
            return self.all()
        if user.is_staff:
            return self.filter(Q(service__created_by=user) | Q(client=user) | Q(email_to=user.email))
        # return self.filter(Q(client=user) | Q(email_to=user.email))
        return self.filter(client=user)

    def get_service_job(self, user, service):
        """
        Returns jobs filtered by service, according to following access rule:
        * user is simply registered, return its jobs, filtered by service
        :param user: currently logged in user
        :param service: service model object to filter
        :return: QuerySet
        """
        if user.is_superuser or user.is_staff:
            return self.filter(submission__service__in=[service, ])
        return self.filter(client=user, submission__service__in=[service, ])

    def get_pending_jobs(self, user=None):
        """
        Return pending jobs for user, according to following access rule:
        * user is simply registered, return its jobs, filtered by service
        :param user: currently logged in user
        :return: QuerySet

        .. note::
            Pending jobs are all jobs which are 'Created', 'Prepared', 'Queued', 'Running'
        """
        if user is not None:
            if user.is_superuser or user.is_staff:
                # return all pending jobs
                return self.filter(status__in=(
                    waves.adaptors.const.JOB_CREATED, waves.adaptors.const.JOB_PREPARED, waves.adaptors.const.JOB_QUEUED,
                    waves.adaptors.const.JOB_RUNNING))
            # get only user jobs
            return self.filter(status__in=(waves.adaptors.const.JOB_CREATED, waves.adaptors.const.JOB_PREPARED,
                                           waves.adaptors.const.JOB_QUEUED, waves.adaptors.const.JOB_RUNNING),
                               client=user)
        # User is not supposed to be None
        return self.none()

    def get_created_job(self, extra_filter, user=None):
        """
        Return pending jobs for user, according to following access rule:
        * user is simply registered, return its jobs, filtered by service
        :param extra_filter: add an extra filter to queryset
        :param user: currently logged in user
        :return: QuerySet
        """
        if user is not None:
            self.filter(status=waves.adaptors.const.JOB_CREATED,
                        client=user,
                        **extra_filter).order_by('-created')
        return self.filter(status=waves.adaptors.const.JOB_CREATED, **extra_filter).order_by('-created').all()


class JobInputManager(models.Manager):
    """ JobInput model Manager """

    def get_by_natural_key(self, job, name):
        return self.get(job=job, name=name)

    def create(self, **kwargs):
        sin = kwargs.pop('srv_input', None)
        if sin:
            kwargs.update(dict(name=sin.name, type=sin.type, param_type=sin.cmd_line_type, label=sin.label))
        return super(JobInputManager, self).create(**kwargs)


class JobOutputManager(models.Manager):
    """ JobInput model Manager """

    def get_by_natural_key(self, job, name):
        return self.get(job=job, _name=name)

    def create(self, **kwargs):
        sout = kwargs.pop('srv_output', None)
        if sout:
            assert isinstance(sout, SubmissionOutput)
            kwargs.update(dict(_name=sout.name, type=sout.type, may_be_empty=sout.optional))
        return super(JobOutputManager, self).create(**kwargs)


class JobHistoryManager(models.Manager):
    def create(self, **kwargs):
        """ Force 'is_admin' flag for JobAdminHistory models objects
        :return: a JobAdminHistory object
        """
        if 'message' not in kwargs:
            kwargs['message'] = kwargs.get('job').message
        return super(JobHistoryManager, self).create(**kwargs)


class JobAdminHistoryManager(JobHistoryManager):
    def get_queryset(self):
        """
        Specific query set to filter only :class:`waves.models.jobs.JobAdminHistory` objects
        :return: QuerySet
        """
        return super(JobAdminHistoryManager, self).get_queryset().filter(is_admin=True)

    def create(self, **kwargs):
        """ Force 'is_admin' flag for JobAdminHistory models objects
        :return: a JobAdminHistory object
        """
        kwargs.update({'is_admin': True})
        return super(JobAdminHistoryManager, self).create(**kwargs)
