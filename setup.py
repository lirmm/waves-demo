import os

from setuptools import setup, find_packages


def get_version():
    import imp
    waves = imp.load_source('waves', os.path.join(os.path.dirname(__file__), 'src', 'waves', 'apps.py'))
    try:
        _version = waves.__version__
        _version_detail = waves.__version_detail__
        _dist_name = waves.__name__
    except ImportError:
        _version = None
        _version_detail = None
        _dist_name = None
    return _version, _version_detail, _dist_name


version, version_detail, sdist_name = get_version()

setup(
    name='waves-demo',
    version=version,
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
        'waves-adaptors>=0.1.0',
        'django-admin-sortable2==0.6.10',
        'django-bootstrap_themes==3.3.6',
        'django-constance==2.0.0',
        'django-countries==4.1',
        'django-crispy-forms==1.6.1',
        'easy_thumbnails==2.3',
        'django-mail-templated==2.6.5',
        'djangorestframework==3.5.4',
        'swapper==1.1.0'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.9.8',
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
