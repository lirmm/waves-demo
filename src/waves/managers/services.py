from __future__ import unicode_literals

import logging
from django.db import models
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
        return self.exclude(authorized_clients__in=[client.pk], status__lt=waves.const.SRV_TEST)

    def get_public_services(self, user=None):
        """
        Returns:
        """
        if user is not None and (user.is_superuser or user.is_staff):
            return self.all()
        else:
            return self.filter(status=waves.const.SRV_PUBLIC)

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
