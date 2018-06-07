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

1. Install WAVES-Demo
---------------------

    1.1 Install From sources, clone our repository:

        ``git clone https://github.com/lirmm/waves-demo/ [waves_dir]``

        or download archive at https://github.com/lirmm/waves-demo/ and uncompress the archive in your destination directory ([waves_dir])

    1.2 Install requirements:

        - ``$ cd [waves_dir]``
        - ``[waves_dir]$ virtualenv .venv``
        - ``[waves_dir]$ source .venv/bin/activate``
        - ``(.venv)[waves_dir]]$ pip install -r requirements.txt``
        - ``(.venv)[waves_dir]]$ pip install -r requirements/production.txt`` (for production)
        - ``(.venv)[waves_dir]]$ pip install -r requirements/mysql.txt`` (for mysql DB layer)

    .. note::

        Use other than SqlLite default DB layer:

        You need to install the Python and MySQL development headers and libraries like so:

        - sudo apt-get install python-dev default-libmysqlclient-dev # Debian / Ubuntu
        - sudo yum install python-devel mysql-devel # Red Hat / CentOS
        - brew install mysql-connector-c # macOS (Homebrew) (Currently, it has bug. See below)

        On Windows, there are binary wheels you can install without MySQLConnector/C or MSVC.

        Then install pip mysql package in your virtualenv:

            ``pip install mysqlclient``

    .. seealso::

        https://docs.djangoproject.com/fr/1.11/ref/databases/


    1.3 Configuration files:

        1.3.0 WAVES env configuration file:

            - ``(.venv)[waves_dir]$ cd src/waves_demo/settings/``
            - ``(.venv)[waves_dir]/src/waves_demo/settings$ cp local.sample.env local.env``
            - edit this local.env file, minimal setup requires these parameters:

                - SECRET_KEY=your-secret-key-to-keep-secret
                - REGISTRATION_SALT=generate-your-key
                - ALLOWED_HOSTS=your-host-name (Ex: localhost, 127.0.0.1 for testing purpose)

        1.3.1 Set up database:

            If not setup, default database is used ~/[waves_dir]/waves.sample.sqlite3

            You can set your own database connection string with DATABASE_URL line

            .. seealso::
                http://django-environ.readthedocs.io/en/latest/


    1.5: Check everything is well (return to [waves_dir]/src/).

            ``(.venv)[waves_dir]/src/$ ./manage.py check``

            To See your configuration with:

            ``(.venv)[waves_dir]/src/$ ./manage.py waves config``

    1.6: Create database:

        ``(.venv)[waves_dir]/src/$ ./manage.py makemigrations``

        ``(.venv)[waves_dir]/src/$ ./manage.py migrate``


    1.7: Load sample data into your database (optional):

            - Demo database is initially setup from:

                ``(.venv)[waves_dir]/src/$ ./manage.py loaddata demo/fixtures/init.json``


    1.8 Test your server (locally):

        - ``(.venv)[waves_dir]/src/$ ./manage.py runserver [ServerIP:ServerPort] --insecure``


    1.9 Start WAVES daemons (in another shell):

        - ``(.venv)[waves_dir]/src/$ ./manage.py wqueue start``
        - ``(.venv)[waves_dir]/src/$ ./manage.py wpurge start``

        .. note::

        wqueue and wpurge command allow you to control daemon, available commands are start|stop|status


2. Configure the production web server:
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
