.. _service-label:

Services
========

Services are the main entry point for WAVEs application, managed by :ref:`service-manager-label`.


    .. autoclass:: waves.models.services.Service
        :members:
        :undoc-members:
        :show-inheritance:

.. _service-inputs-label:

Service Inputs
--------------
    - Base class for service inputs shared information
    .. autoclass:: waves.models.services.BaseInput
        :members:
    - Classic Service input
    A Service input may be a file, text, int, bool, float, list of values

    .. autoclass:: waves.models.services.ServiceInput
        :members:
    - Related Inputs:
    Input may be related to value specified from another one, this class represent this behaviour

    .. autoclass:: waves.models.services.RelatedInput
        :members:

.. _service-outputs-label:

Service Outputs:
----------------
Service description defines expected outputs from Service job runs

    .. autoclass:: waves.models.services.ServiceOutput
        :members:


.. _service-samples-label:

Samples
-------
Services may provide sample data for their submissions

    .. autoclass:: waves.models.samples.ServiceInputSample
        :members:
        :undoc-members:
        :show-inheritance:

    .. autoclass:: waves.models.samples.ServiceSampleDependentsInput
        :members:
        :undoc-members:
        :show-inheritance: