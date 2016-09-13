Quick Start Installation process
================================

1. RAVEN needs to be installed within a django project, see Django
   framework documentation if needed.

2. Install waves package with pip (strongly recommended to do so in a
   dedicated virtualenv):

   ``pip install waves``

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


