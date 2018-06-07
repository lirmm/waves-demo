Installation
============

GET a WAVES demo website following the next few steps. WAVES can run with Apache or Nginx with uWSGI

.. WARNING::
    To run WAVES, it is strongly recommended to setup a dedicated user. Indeed, WAVES uses
    `saga-python <https://github.com/radical-cybertools/saga-python/>`_.
    This module will try to create directories (.radical and .saga) for which another user (such as www-data) might not have the rights to do so.


0. Prerequisites
----------------
    .. note::
        In order to install WAVES you will need:
            - python 2.7.X (WAVES is not yet compatible with python 3.5)
            - pip package manager
            - A web server: `Apache <https://httpd.apache.org/>`_ or `NGINX <https://nginx.org/>`_
            - A database backend (Mysql or Postgres) but by default WAVES runs with sqlite

    0.1 Install From sources, clone our repository:

        ``git clone https://github.com/lirmm/waves-demo/ [waves_dir]``

        or download archive at https://github.com/lirmm/waves-demo/ and uncompress the archive in your destination directory ([waves_dir])

    0.2 Install requirements:

        - ``$ cd [waves_dir]``
        - ``[waves_dir]$ virtualenv .venv``
        - ``[waves_dir]$ source .venv/bin/activate``
        - ``(.venv)[waves_dir]]$ pip install -r requirements.txt``
        - ``(.venv)[waves_dir]]$ pip install -r requirements/production.txt`` (for production)
        - ``(.venv)[waves_dir]]$ pip install -r requirements/mysql.txt`` (for mysql DB layer)


1. Install WAVES-Demo
---------------------

    1.1 Configuration files:

        - WAVES env configuration file:

            - ``(.venv)[waves_dir]$ cd src/waves_demo/settings/``
            - ``(.venv)[waves_dir]/src/waves_demo/settings$ cp local.sample.env local.env``
            - minimal setup requires these parameters:

                - SECRET_KEY=your-secret-key-to-keep-secret
                - REGISTRATION_SALT=generate-your-key
                - ALLOWED_HOSTS=your-host-name (Ex: localhost, 127.0.0.1 for testing purpose)
            - you can set up as well your db connection params here (or in classical "DJANGO way" settings if you want)

    1.2 Set up database:

        - Check parameters with: ``(.venv)[waves_dir]/src/$ ./manage.py check`` (pip install any missing dependencies)
        - See your configuration with: ``(.venv)[waves_dir]/src/$ ./manage.py waves config``
        - If no setup, default database is used ~/[waves_dir]/waves.sample.sqlite3

        1.2.1: Setup your database connection string (if not using sqlite default)

            - Create local.env (copy from local.env.sample located in waves_demo/settings/)
            - Setup line corresponding to your needs (DATABASE_URL)

        1.2.2: Check everything is well.

            ``(.venv)[waves_dir]/src/$ ./manage.py check``

        1.2.3: Create migration files:

            .. note::

                If you see this message:

                .. code-block:: bash

                    You are trying to add a non-nullable field 'service' to demowavessubmission without a default; we can't do that (the database needs something to populate existing rows).
                    Please select a fix:
                    1) Provide a one-off default now (will be set on all existing rows with a null value for this column)
                    2) Quit, and let me add a default in models.py

                => Select 1) option and set up default value to '1' (this problem is due to swapping of default Service and Submission)

            - Create your database: ``(.venv)[waves_dir]/src/$ ./manage.py migrate``
            - Create Superadmin user: ``(.venv)[waves_dir]/src/$ ./manage.py createsuperuser``

        1.2.4: Load sample data into your database (optional):

            - Demo database is initially setup from:

                ``(.venv)[waves_dir]/src/$ ./manage.py loaddata demo/fixtures/init.json``


    1.3 Test your server (locally):

        - ``(.venv)[waves_dir]/src/$ ./manage.py runserver [ServerIP:ServerPort] --insecure``


    1.4 Start WAVES daemons:

        - ``(.venv)[waves_dir]/src/$ ./manage.py wqueue start``
        - ``(.venv)[waves_dir]/src/$ ./manage.py wpurge start``

        .. note::

        wqueue and wpurge command allow you to control daemon, available commands are start|stop|status


2. Configure the web server:
-----------------------------

    2.1 Production settings:

        - Create staticfiles ``(.venv)[waves_dir]/src/$ ./manage.py collectstatic``
        - Setup your server following instruction `Django Docs <https://docs.djangoproject.com/fr/1.11/howto/deployment/wsgi/>`_

        .. seealso:: UWSGI configuration at `<http://uwsgi-docs.readthedocs.io/>`_

        .. seealso:: APACHE `<http://uwsgi-docs.readthedocs.io/en/latest/Apache.html>`_

        .. seealso:: NGINX `<http://uwsgi-docs.readthedocs.io/en/latest/tutorials/Django_and_nginx.html>`_


    .. warning::

        You might experience some troubles with directories permissions when installing WAVES-demo on your web server
        on some directories:
        logs, jobs, data, binaries directories must be writable both from web user/group (www-data or apache) and by the user which launch the queue.
