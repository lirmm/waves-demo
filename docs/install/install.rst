Install WAVES
-------------

These are the steps you should car about when installing waves on your web server.
WAVES can run on Apache with wsgi, or with uwsgi.


Get WAVES application
----------------------
0. Prerequisites:
    In order to install WAVES you will need:
    - python 2.7.X
    - pip
    - virtualenv (or virtualenvwrapper)
    - a web server such as Apache or Nginx
    - (Optional) a database backend Mysql, Oracle, Postgres (WAVES use a sqlite database by default)

1. Install source :
    Choose in one of these methods
    - pip install waves
    - git clone git://git.renater.fr/waves.git
    - Download archive at : [URL ARCHIVE tag.gz]
        - uncompress the archive in your destination dir ([INSTALL_DIR])

2. Create virtual env dedicated to WAVES:
    - youruser@yourmachine:___$ cd [INSTALL_DIR]
    - youruser@yourmachine:[INSTALL_DIR]$ virtualenv [ENV_NAME]
    - youruser@yourmachine:[INSTALL_DIR]$ source [ENV_NAME]/bin/activate (or specific activation script if needed see [link:virtualenv doc]

3. Install WAVES requirements:
    - ([ENV_NAME])youruser@yourmachine:[INSTALL_DIR]$ pip install -r requirements.txt

4. Configuration files:
    - ([ENV_NAME])youruser@yourmachine:[INSTALL_DIR]$ cd src/waves_services/
    - ([ENV_NAME])youruser@yourmachine:[INSTALL_DIR]/src/waves_services$ mv waves.env.sample waves.env
    - Edit your waves.env file to set WAVES parameters ([link:waves parameters])

3. Create database and initialize some data:
    - ([ENV_NAME])youruser@yourmachine:[INSTALL_DIR]$ cd src
    - ([ENV_NAME])youruser@yourmachine:[INSTALL_DIR]/src$ python manage.py makemigrations eav
    - ([ENV_NAME])youruser@yourmachine:[INSTALL_DIR]/src$ python manage.py migrate
    - ([ENV_NAME])youruser@yourmachine:[INSTALL_DIR]/src$ python manage.py loaddata /fixtures/init.json

4. Test your env:
    - ([ENV_NAME])youruser@yourmachine:[INSTALL_DIR]/src$ python manage.py runserver [link: runserver django doc]
    - You should be able to see home page on : http://127.0.0.1:8000/
    - Remember this command is not dedicated to be used un production environment

5. Configure your web server to activate WAVES:
    - For Apache: see section [link: Apache]
    - For Nginx: see section [link: Nginx]
    - StandAlone uwsgi [link: uwsgi Doc] (not recommended for production):
        - pip install uwsgi
        - edit waves_uwsgi.ini.sample and rename to waves_uwsgi.ini
        - launch uwsgi waves_uwsgi.ini

Apache virtual host configuration example
-----------------------------------------
<VirtualHost *:80>

    ServerName dev.waves.atgc-montpellier.fr
    ServerAlias waves.atgc-montpellier.fr
    ServerAdmin webmaster@atgc-montpellier.fr

    DocumentRoot /home/www/waves

    <Directory /home/www/waves>
      Options +Indexes
      Require all granted
    </Directory>

    <Directory /home/www/staticfiles>
      Options +Indexes
      Require all granted
    </Directory>

########################## UWSGI MODE ###########################
    <Location />
      Options +Indexes
      SetHandler uwsgi-handler
      uWSGISocket 127.0.0.1:3031
    </Location>
########################## /UWSGI MODE ###########################
########################## APACHE WSGI MODE ###########################
# SetEnv DJANGO_SETTINGS_MODULE waves_services.settings.production
# WSGIDaemonProcess waves_services python-path=/home/marc/.virtualenvs/wave/srcs:/home/marc/.virtualenvs/waves/lib/python2.7/site-packages:/home/www/waves
# WSGIProcessGroup waves_services
# WSGIScriptAlias / /home/www/waves/waves_services/wsgi.py
#    <Directory /home/www/waves/waves_services>
#      Options FollowSymLinks Indexes
#      <Files wsgi.py>
#	Require all granted
#      </Files>
#    </Directory>
########################## /APACHE WSGI MODE ###########################
    <Location /static/>
      SetHandler None
    </Location>
    <Location /media/>
      SetHandler None
    </Location>
    Alias /media /home/www/waves/media/
    Alias /static /home/www/staticfiles

    ErrorLog /home/www/logs/waves.apache.error.log
    LogLevel info
    CustomLog /home/www/logs/waves.acces.log combined




</VirtualHost>


