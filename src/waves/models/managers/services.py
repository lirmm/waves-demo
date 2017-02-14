from __future__ import unicode_literals

from django.db import models
from django.db.models import Q
from mptt.managers import TreeManager

__all__ = ['ServiceRunParamManager', 'ServiceCategoryManager', 'ServiceManager']

class ServiceRunParamManager(models.Manager):
    def get_by_natural_key(self, service, param):
        return self.get(service=service, param=param)

    def get_queryset(self):
        return super(ServiceRunParamManager, self).get_queryset()


class ServiceCategoryManager(TreeManager):
    def get_by_natural_key(self, api_name):
        return self.get(api_name=api_name)


class ServiceManager(models.Manager):
    """
    Service Model 'objects' Manager
    """

    def get_services(self, user=None, for_api=False):
        """

        :param user: current User
        :param for_api: filter only waves_api enabled, either return only web enabled
        :return: QuerySet for services
        :rtype: QuerySet
        """
        if user is not None and not user.is_anonymous():
            if user.is_superuser:
                queryset = self.all()
            elif user.is_staff:
                # Staff user have access their own Services and to all 'Test / Restricted / Public' made by others
                queryset = self.filter(
                    Q(status=self.model.SRV_DRAFT, created_by=user) |
                    Q(status__in=(self.model.SRV_TEST, self.model.SRV_RESTRICTED,
                                  self.model.SRV_PUBLIC))
                )
            else:
                # Simply registered user have access only to "Public" and configured restricted access
                queryset = self.filter(
                    Q(status=self.model.SRV_RESTRICTED, restricted_client__in=(user,)) |
                    Q(status=self.model.SRV_PUBLIC)
                )
        # Non logged in user have only access to public services
        else:
            queryset = self.filter(status=self.model.SRV_PUBLIC)
        if for_api:
            queryset = queryset.filter(api_on=True)
        else:
            queryset = queryset.filter(web_on=True)
        return queryset

    def get_api_services(self, user=None):
        """ Return all waves_api enabled service to User
        """
        return self.get_services(user, for_api=True)

    def get_web_services(self, user=None):
        """ Return all web enabled services """
        return self.get_services(user)

    def get_by_natural_key(self, api_name, version, status):
        return self.get(api_name=api_name, version=version, status=status)
