============
Installation
============

These are the steps you should care about when installing waves on your web server.
WAVES can run on Apache, Nginx, uWSGI .


Get WAVES application
----------------------

    0. Prerequisites:
        In order to install WAVES you will need:
        - python 2.7.X
        - pip
        - dedicated virtualenv is strongly recommended
        - a web server: Apache or NGINX
        - (Optional) a database backend Mysql, Oracle, Postgres (WAVES use a sqlite3 database by default)

    1. Install
        - git clone https://github.com/lirmm/mab/waves/

            use master / stable release at first, but if you feel lucky, you can try to switch to 'devel' branch for last version

        - Download archive at : https://github.com/lirmm/mab/waves/:

            uncompress the archive in your destination dir ([INSTALL_DIR])

    2. Create virtual env dedicated to WAVES:
        - youruser@yourmachine:___$ cd [INSTALL_DIR]
        - youruser@yourmachine:[INSTALL_DIR]$ virtualenv [ENV_NAME]
        - youruser@yourmachine:[INSTALL_DIR]$ source [ENV_NAME]/bin/activate

    3. Install WAVES requirements:
        - ::: Your need to have git installed in order to get all dependencies :::
        - ([ENV_NAME])youruser@yourmachine:[INSTALL_DIR]$ pip install -r requirements.txt

    4. Configuration files:
        4.1 Global configuration file (classic Django stuff):
            - rename waves_services/settings/local.sample.env to local.env
            - set up a minima required parameters :
                - SECRET_KEY=your-secret-key-to-keep-secret
                - REGISTRATION_SALT=generate-your-key
                - ALLOWED_HOSTS=your-host-name
        4.2 WAVES specifi configuration file:
            You might not need to modify anything to basic configuration, but some usefull parameters can be set up
            your conf:
            - ([ENV_NAME])youruser@yourmachine:[INSTALL_DIR]$ cd config/
            - ([ENV_NAME])youruser@yourmachine:[INSTALL_DIR]/config$ mv waves.env.sample waves.env
            - Edit your waves.env file to set WAVES parameters ([link:waves parameters])

        4.3 Check parameters with : [INSTALL_DIR]/src/manage.py check and [INSTALL_DIR]/src/manage.py wavesconfig
        4.4 Collect staticfiles : [INSTALL_DIR]/src/manage.py collectstatics

    3. You plan to use default database layer configuration:

        3.1 If your are NOT using WAVES sample database and want to insert data in your own :
        Create database and initialize some data:
        - ([ENV_NAME])youruser@yourmachine:[INSTALL_DIR]$ cd src
        - ([ENV_NAME])youruser@yourmachine:[INSTALL_DIR]/src$ python manage.py makemigrations eav
        - ([ENV_NAME])youruser@yourmachine:[INSTALL_DIR]/src$ python manage.py migrate
        - ([ENV_NAME])youruser@yourmachine:[INSTALL_DIR]/src$ python manage.py loaddata waves/fixtures/init.json

        3.2 If you use WAVES sample database:
        - be sure your 'Web' user has write access to sample db file (waves.sample.sqlite3)

    4. Configure your web server to activate WAVES:
        - For Apache: see section [link: Apache]
        - For Nginx: see section [link: Nginx]
        - StandAlone uwsgi [link: uwsgi Doc] (not recommended for production):
            - pip install uwsgi
            - edit waves_uwsgi.ini.sample and rename to waves_uwsgi.ini
            - launch uwsgi waves_uwsgi.ini

Web Server configuration
------------------------
    - almost ready-to-go apache configuration template is available in src/waves/config/waves.apache.conf.sample
    - almost ready-to-go uwsgi configuration template is available in src/waves/config/waves_uwsgi.ini.sample

    Feel free to use them according to your server.
