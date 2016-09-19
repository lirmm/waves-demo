from __future__ import unicode_literals

import logging
from django.db import models
from django.db.models import Q
import waves.const
from waves.exceptions import *

logger = logging.getLogger(__name__)
__all__ = ['ServiceManager', 'WebSiteMetaMngr', 'DocumentationMetaMngr', 'DownloadLinkMetaMngr', 'FeatureMetaMngr',
           'MiscellaneousMetaMngr', 'CitationMetaMngr', 'CommandLineMetaMngr']


class ServiceManager(models.Manager):

    def get_services(self, user=None, for_api=None):
        """
        Returns:
        """
        if user is not None:
            if user.is_superuser:
                # Super user has access to 'all' services / submissions etc...
                queryset = self.all()
            elif user.is_staff:
                # Staff user have access their own Services and to all 'Test / Restricted / Public' made by others
                queryset = self.filter(
                    Q(status=waves.const.SRV_DRAFT, created_by=user) |
                    Q(status__in=(waves.const.SRV_TEST, waves.const.SRV_RESTRICTED, waves.const.SRV_PUBLIC))
                )
            else:
                # Simply registered user have access only to "Public" and configured restricted access
                queryset = self.filter(
                    Q(status=waves.const.SRV_RESTRICTED, restricted_client__in=(user.profile,)) |
                    Q(status=waves.const.SRV_PUBLIC)
                )
        # Non logged in user have only access to public services
        else:
            queryset = self.filter(status=waves.const.SRV_PUBLIC)
        if for_api:
            queryset.filter(api_on=True)
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug('Generated query set \n%s', queryset.query)
            logger.debug('Should return this services:\n%s', queryset.all())
        return queryset

    def get_api_services(self, user=None):
        return self.get_services(user, for_api=True)

    def get_web_services(self, user=None):
        return self.get_services(user)


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
