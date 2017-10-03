import inspect
import os
import sys

from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

src_folder = os.path.realpath(
    os.path.abspath(os.path.join(os.path.split(inspect.getfile(inspect.currentframe()))[0], "src")))

if src_folder not in sys.path:
    sys.path.insert(0, src_folder)


def import_version():
    from demo import __version__
    return __version__


os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='waves-demo',
    version=import_version(),
    packages=find_packages('src'),
    include_package_data=True,
    package_dir={'': 'src', },
    url='https://github.com/lirmm/waves-demo',
    license='GPL-v3',
    author='Marc Chakiachvili, Floreal Cabanattes, Vincent Berry, Anne-Muriel Arigon Chifolleau',
    author_email='marc.chakiachvili@gmail.com, '
                 'floreal.cabanettes@lirmm.fr, '
                 'vincent.lefort@lirmm.fr, '
                 'vincent.berryr@lirmm.fr, '
                 'anne-muriel.arigon@lirmm.fr',
    description='WebApp for Versatile and Easy bio-informatics Services',
    maintainer='LIRMM - MAB Laboratory - France',
    maintainer_email='vincent.lefort@lirmm.fr',
    install_requires=[
        'django==1.11.5',
        'django-admin-sortable2==0.6.10',
        'django-bootstrap_themes==3.3.6',
        'django-constance==2.0.0',
        'django-countries==4.1',
        'django-crispy-forms==1.6.1',
        'easy_thumbnails==2.3',
        'django-mail-templated==2.6.5',
        'djangorestframework==3.5.4',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.9',
        'Development Status :: 1 - Dev/Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GPLv3 License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Utilities',
        'Topic :: Web :: Distributed Computing',
        'Topic :: Scientific/Engineering :: Interface Engine/Protocol',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Operating System :: Unix'
    ],

)
