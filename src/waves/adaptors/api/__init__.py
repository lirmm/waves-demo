# -*- coding: utf-8 -*-
""" API remotes calls based Adaptors modules """
from __future__ import unicode_literals

from galaxy.tool import GalaxyJobAdaptor
from galaxy.workflow import GalaxyWorkFlowAdaptor
from waves.adaptors.api.compphy.adaptor import CompPhyApiAdaptor

__all__ = [str('GalaxyJobAdaptor'),
           str('GalaxyWorkFlowAdaptor'),
           str('CompPhyApiAdaptor')]

__group__ = "API"
__author__ = "Marc Chakiachvili"
__version__ = '0.1.0'