Quick Start Installation
========================

1. WAVES needs to be installed within a django project, see Django
   framework documentation if needed.

2. Install waves package with pip (strongly recommended to do so in a
   dedicated virtualenv):

   ``pip install waves``

3. Add "waves" to your INSTALLED_APPS settings::

    INSTALLED_APPS = [
        ...
        'waves',
        ...
    ]

4. Include the services urls in your project urls.py::

    url('^waves/', include('waves.urls'))



   Alternativly you can use only urls configuration you need::


    url(r'^$', HomePage.as_view(), name='home'),
    url(r'^accounts/', include('waves.urls.accounts_url')),
    url(r'^waves/api/', include('waves.urls.api_urls')),
    url(r'^admin/', include('waves.urls.back_urls')),
    url(r'^waves/', include('waves.urls.front_urls'))

5. Run ``python manage.py migrate`` to install database models.


6. Run ``python manage.py waves `` to
   import sample data if you wish


7. Start the development server, ``python manage.py runserver``: visit
   ``http://127.0.0.1:8000/services/ to start your services``


