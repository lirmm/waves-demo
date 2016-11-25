# -*- coding: utf-8 -*-
""" API remotes calls based Adaptors modules """
from __future__ import unicode_literals

from galaxy.tool import GalaxyJobAdaptor
from galaxy.workflow import GalaxyWorkFlowAdaptor
from compphy import CompPhyApiAdaptor

__all__ = [str('GalaxyJobAdaptor'),
           str('GalaxyWorkFlowAdaptor'),
           str('CompPhyApiAdaptor')]
