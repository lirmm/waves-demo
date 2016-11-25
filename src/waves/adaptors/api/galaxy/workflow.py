from __future__ import unicode_literals

from waves.adaptors.api.galaxy.tool import GalaxyJobAdaptor
grp_name = "Galaxy"


class GalaxyWorkFlowAdaptor(GalaxyJobAdaptor):
    """Dedicated Adaptor to run / import / follow up Galaxy Workflow execution

    .. WARNING::
        This class is not fully implemented at the moment !

    As it inherit from :class:`waves.adaptors.GalaxyJobAdaptor`, its init paramas are the same.

    """
    name = 'Galaxy remote workflow adaptor (api_key)'

    #: Dedicated import clazz for Galaxy workflows see :class:`waves.adaptors.importer.galaxy.GalaxyWorkFlowImporter`
    importer_clazz = 'waves.importers.galaxy.workflow.GalaxyWorkFlowImporter'

    def _run_job(self, job):
        """
        :param job: Job to run
        :raise: NotImplementedError
        """
        raise NotImplementedError()

    def _cancel_job(self, job):
        """
        :param job: Job to cancel
        :raise: NotImplementedError
        """
        raise NotImplementedError()

    def _job_status(self, job):
        """
        :param job: Job to show status
        :raise: NotImplementedError
        """
        raise NotImplementedError()

    def _job_results(self, job):
        """
        :param job: Job to retrieve result for
        :raise: NotImplementedError
        """
        raise NotImplementedError()