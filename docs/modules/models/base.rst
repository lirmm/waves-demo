Waves Demo classes
==================

WAVES Demo extends base Waves-Core functionality

.. seealso::
    Waves-Core Documentation `<http://waves-core.readthedocs.io/en/latest/modules/source.html>`_

Service override example
------------------------

.. autoclass:: demo.models.DemoWavesService
    :members:

Submission override example
---------------------------

.. autoclass:: demo.models.DemoWavesSubmission
    :members:

Adapters override example
-------------------------

Demo adapters are not meant to execute anything for real, but are intended to demonstrate how to configure them in backoffice
So every standard Wcore adapter is overriden in order to mock their execution on Demo platform

.. autoclass:: demo.adaptors.WavesDemoAdaptor
    :private-members:
    :special-members:

.. autoclass:: demo.adaptors.GalaxyJobAdaptor
    :private-members:

.. autoclass:: demo.adaptors.GalaxyJobAdaptor
    :private-members:
