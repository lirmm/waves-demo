from __future__ import unicode_literals
from waves.runners.drmaa import DRMAAJobRunner
import os
import logging
from django.conf import settings
import waves.const

logger = logging.getLogger(__name__)


class SGEJobRunner(DRMAAJobRunner):

    sge_root = settings.WAVES_SGE_ROOT
    sge_cell = settings.WAVES_SGE_CELL

    @property
    def init_params(self):
        base = super(SGEJobRunner, self).init_params
        base.update(dict(sge_root=self.sge_root, sge_cell=self.sge_cell))
        return base

    def __init__(self, **kwargs):
        if 'sge_root' in kwargs:
            logger.info('Overriding SGE_ROOT due to runner plugin parameter: %s',
                        kwargs['sge_root'])
            self.sge_root = kwargs['sge_root']

        if 'sge_cell' in kwargs:
            logger.info('Overriding SGE_CELL due to runner plugin parameter: %s',
                        kwargs['sge_cell'])
            self.sge_cell = kwargs['sge_cell']
        super(SGEJobRunner, self).__init__(**kwargs)
        os.environ['SGE_ROOT'] = self.sge_root
        os.environ['SGE_CELL'] = self.sge_cell
