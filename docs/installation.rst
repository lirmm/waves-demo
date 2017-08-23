Installation
============

GET a WAVES web-app online following the next few steps, WAVES can run on Apache, Nginx with uWSGI

.. WARNING::
    To run WAVES, it's strongly recommended that you setup a dedicated user, because WAVES run with
    saga-python, and this module need to create some directories you might not be able to create (.radical and .saga)
    with another user (such as www-data)


0. Prerequisites
----------------
    .. note::
        In order to install WAVES you will need:
            - python 2.7.X (WAVES should be compatible with python 3.5 but not fully tested)
            - pip package manager
            - A web server: `Apache <https://httpd.apache.org/>`_ or `NGINX <https://nginx.org/>`_
            - A database backend (Mysql or Postgres) but WAVES could run with sqlite DB

    0.1 Get the sources:
        - Clone our repository:
            git clone https://github.com/lirmm/waves-demo/ [waves_dir]

        - Download archive:
            Download archive at https://github.com/lirmm/waves-demo/ and uncompress the archive in your destination dir ([waves_dir])

    0.2 Create virtual env:
        - ``$ cd [waves_dir]``
        - ``[waves_dir]$ virtualenv .venv``
        - ``[waves_dir]$ source .venv/bin/activate``
        - ``(.venv)[waves_dir]]$ pip install -r requirements.txt``
        - ``(.venv)[waves_dir]]$ pip install -e git+https://github.com/lirmm/waves-core.git#egg=waves``

1. Install WAVES
----------------

    1.1 Configuration files:
        - WAVES env configuration file:
            - ``(.venv)[waves_dir]$ cd src/waves_demo/settings/``
            - ``(.venv)[waves_dir]/src/waves_demo/settings$ cp local.sample.env local.env``
            - minimal setup requires these parameters:
                - SECRET_KEY=your-secret-key-to-keep-secret
                - REGISTRATION_SALT=generate-your-key
                - ALLOWED_HOSTS=your-host-name (Ex: localhost,
            - you can set up as well your db connection params here (or ing classsical DJANGO settings if you want)

    1.2 Set up database:
        - Setup default log dir: ``(.venv)[waves_dir]/src/$ mkdir ..logs``
        - Create your database: ``(.venv)[waves_dir]/src/$ ./manage.py migrate``
        - Create Superadmin user: ``(.venv)[waves_dir]/src/$ ./manage.py createsuperuser``
        - Create staticfiles: ``(.venv)[waves_dir]/src/$ ./manage.py collecstatic``
        - Initialize some required data: ``(.venv)[waves_dir]/src/$ ./manage.py wavesadmin init``
        - Check parameters with: ``(.venv)[waves_dir]/src/$ ./manage.py check``
        - See your configuration with: ``(.venv)[waves_dir]/src/$ ./manage.py wavesadmin config``


2. Configure your web server:
-----------------------------

    2.1 UWSGI:
        - Sample file is located under src/waves/config/waves_uwsgi.ini.sample
        - Rename/Edit according to your settings
        - more information `<http://uwsgi-docs.readthedocs.io/>`_

        .. seealso::
            Init script is available in src/waves/config/uwsgi.conf in order to automatically start WAVES on server
            start-up


    2.1 APACHE:
        - Sample file is located under src/waves/config/waves.apache.conf.sample
        - Rename/Edit according to your settings
        - Add it to Apache enabled conf

        .. seealso:: `<http://uwsgi-docs.readthedocs.io/en/latest/Apache.html>`_

    2.2 NGINX:
        - Sample file is located under src/waves/config/waves.nginx.conf.sample
        - Rename/Edit according to your settings
        - Add it to nginx enabled conf

        .. seealso:: `<http://uwsgi-docs.readthedocs.io/en/latest/tutorials/Django_and_nginx.html>`_


