Installation
============

GET a WAVES web-app online following the next few steps, WAVES can run on Apache, Nginx, uWSGI

Prerequisites
----------------------
In order to install WAVES you will need:
    - python 2.7.X (not sure if WAVES is fully compatible with python 3!)
    - pip or easy_install
    - A web server (obviously): `Apache <https://httpd.apache.org/>`_ or `NGINX <https://nginx.org/>`_
    - Optionally a database backend (Mysql or Postgres) but WAVES comes with its own ready-to-run sqlite3 database

Get the sources
---------------
    - Clone our repository:
        git clone https://github.com/lirmm/waves-webapp/ [waves_dir]
            For production, classically use master, but if you feel lucky, you can try to switch to 'devel' branch for the current latest version
    - Download archive:
        Download archive at https://github.com/lirmm/waves-webapp/ and uncompress the archive in your destination dir ([waves_dir])

Create virtual env
------------------
    - $ ``cd [waves_dir]``
    - [waves_dir]$ ``virtualenv .venv``
    - [waves_dir]$ ``source .venv/bin/activate``

Install WAVES requirements
--------------------------

    .. WARNING::
        **Your need to have git installed in order to get all dependencies**
        - (.venv)[waves_dir]$ ``pip install -r requirements.txt``

Configuration files
--------------------

    - Global configuration file (classic Django stuff):
        - copy **`waves_services/settings/local.sample.env`** to **`local.env`**
        - minimal setup requires these parameters:
            - SECRET_KEY=your-secret-key-to-keep-secret
            - REGISTRATION_SALT=generate-your-key
            - ALLOWED_HOSTS=your-host-name
    - WAVES specific settings: you do not need to modify anything to basic configuration, but some useful parameters can be set up your conf:
        - (.venv)[waves_dir]$ ``cd config/``
        - (.venv)[waves_dir]/config$ ``mv waves.env.sample waves.env``
        - Edit your waves.env file to set WAVES parameters ([link:waves parameters])
    - Check parameters with:

        .. code-block:: python

            [waves_dir]/src/manage.py check
            [waves_dir]/src/manage.py wavesconfig


Static files
------------

Collect staticfiles : ~[waves_dir]$ ``/src/manage.py collectstatic``


1. Create database and initialize some data:

        - (.venv)~[waves_dir]$ ``cd src``
        - (.venv)~[waves_dir]/src$ ``python manage.py migrate``
        - (.venv)~[waves_dir]/src$ ``python manage.py createsuperuser``

    You can load sample data with :
        - (.venv)~[waves_dir]/src$ ``python manage.py loaddata waves/fixtures/init.json``

2. Configure your web server to activate WAVES:
    - For Apache: see section [link: Apache] TOBEDONE
    - For Nginx: see section [link: Nginx] TOBEDONE

Web Server configuration
------------------------
- almost ready-to-go apache configuration template is available in src/waves/config/waves.apache.conf.sample
- almost ready-to-go uwsgi configuration template is available in src/waves/config/waves_uwsgi.ini.sample

Feel free to use them according to your server.
