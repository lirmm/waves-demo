.. WAVES documentation master file, created by
   sphinx-quickstart on Tue Apr 19 13:17:47 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to WAVES's documentation!
=================================

Description
-----------

-  Create and manage bioinformatic tools execution over such platform as
   Galaxy server, DRMAA compliant cluster, Direct script execution, API
   calls to other services...
-  Presents these tools in a frontend based on Bootstrap3
-  Follow and manage remote RESTful API access to your platform.

Quick start
-----------

1. RAVEN needs to be installed within a django project, see Django
   framework documentation if needed.

2. Install waves package with pip (strongly recommended to do so in a
   dedicated virtualenv):

   ``pip install dj-waves``

3. Add "waves" to your INSTALLED\_APPS settings::

   ``INSTALLED\_APPS = [
        'waves',
        ...
    ]``

4. Include the services urls in your project urls.py::

   ``url('^waves/', include('waves.urls')),``

5. Run ``python manage.py migrate`` to install database models.

6. Run ``python manage.py loaddata sample.json --app waves`` to
   import sample data if you wish

7. Start the development server, ``python manage.py runserver``: visit
   ``http://127.0.0.1:8000/services/ to start your services``




.. toctree::
   :maxdepth: 2



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

