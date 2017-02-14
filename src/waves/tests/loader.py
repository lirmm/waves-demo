from __future__ import absolute_import

import inspect
import logging
import unittest

from waves_adaptors.loader import load_core, load_addons, load_importers

logger = logging.getLogger(__name__)


class TestLoadAddons(unittest.TestCase):

    def testLoadActions(self):
        core = load_core()
        self.assertTrue(all([not inspect.isabstract(clazz) for name, clazz in core]))
        [logger.debug(c) for c in core]
        addons = load_addons()
        # There should not be any addons from core project
        self.assertTrue(len(addons) == 0)
        imps = load_importers()
        # There should not be any addons from core project
        self.assertTrue(len(imps) == 0)

