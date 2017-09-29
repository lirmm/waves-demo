Installation
============

GET a WAVES demo website following the next few steps. WAVES can run with Apache or Nginx with uWSGI

.. WARNING::
    To run WAVES, it is strongly recommended to setup a dedicated user. Indeed, WAVES uses
    `saga-python <https://github.com/radical-cybertools/saga-python/>`_. This module will try to create directories (.radical and .saga) for which another user (such as www-data) might not have the rights to do so.


0. Prerequisites
----------------
    .. note::
        In order to install WAVES you will need:
            - python 2.7.X (WAVES is not yet compatible with python 3.5)
            - pip package manager
            - A web server: `Apache <https://httpd.apache.org/>`_ or `NGINX <https://nginx.org/>`_
            - A database backend (Mysql or Postgres) but by default WAVES runs with sqlite

    0.1 Get the sources:
        - Clone WAVES repository:
            git clone https://github.com/lirmm/waves-demo/ [waves_dir]

        - Download archive:
            Download archive at https://github.com/lirmm/waves-demo/ and uncompress the archive in your destination directory ([waves_dir])

    0.2 Create python virtual environment:
        - ``$ cd [waves_dir]``
        - ``[waves_dir]$ virtualenv .venv``
        - ``[waves_dir]$ source .venv/bin/activate``
        - ``(.venv)[waves_dir]]$ pip install -r requirements.txt``

1. Install WAVES
----------------

    1.1 Configuration files:
        - WAVES env configuration file:
            - ``(.venv)[waves_dir]$ cd src/waves_demo/settings/``
            - ``(.venv)[waves_dir]/src/waves_demo/settings$ cp local.sample.env local.env``
            - minimal setup requires these parameters:
                - SECRET_KEY=your-secret-key-to-keep-secret
                - REGISTRATION_SALT=generate-your-key
                - ALLOWED_HOSTS=your-host-name (Ex: localhost, 127.0.0.1 for testing purpose)
            - you can set up as well your db connection params here (or ing classsical DJANGO settings if you want)

    1.2 Set up database:
        - Setup default log dir: ``(.venv)[waves_dir]/src/$ mkdir ..logs``
        - Setup default data dir (if not exists): ``(.venv)[waves_dir]/src/$ mkdir ..data``
        - Check parameters with: ``(.venv)[waves_dir]/src/$ ./manage.py check`` (pip install any missing dependencies)
        - See your configuration with: ``(.venv)[waves_dir]/src/$ ./manage.py waves config``


        - Create your database: ``(.venv)[waves_dir]/src/$ ./manage.py migrate``
        - Create Superadmin user: ``(.venv)[waves_dir]/src/$ ./manage.py createsuperuser``

        1.2.1 If you want a sample service:


    1.3 Test your server:
        - ``(.venv)[waves_dir]/src/$ ./manage.py waves queue start``
        - ``(.venv)[waves_dir]/src/$ ./manage.py runserver --settings=waves_demo.settings.development``

        1.2.1 If you use default database configuration:
            - You may login into backoffice (127.0.0.1:8000) with credentials : demo@demo.fr / demodemo
            - A sample 'cp' service is already given as a starter service template. Running on local server.

2. Configure the web server:
-----------------------------

    2.1 Production settings:

        - Create staticfiles: ``(.venv)[waves_dir]/src/$ ./manage.py collectstatic``
        - Setup your server: `Django Docs <https://docs.djangoproject.com/fr/1.11/howto/deployment/wsgi/>`_

    2.2 UWSGI:
        - Init sample script is available in waves_uwsgi.ini
        - Rename/Edit according to your settings

        .. seealso:: `<http://uwsgi-docs.readthedocs.io/>`_


    2.3 APACHE:

        .. seealso:: `<http://uwsgi-docs.readthedocs.io/en/latest/Apache.html>`_

    2.4 NGINX:
        .. seealso:: `<http://uwsgi-docs.readthedocs.io/en/latest/tutorials/Django_and_nginx.html>`_


