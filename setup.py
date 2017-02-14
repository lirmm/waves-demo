from distutils.core import setup

import os
from setuptools import setup, find_packages
mod_root = "src/waves"


def get_version(mod_root):
    import imp
    # mod_waves = imp.find_module('waves', os.path.join(os.path.dirname(os.path.realpath(__file__))))
    # print mod_waves
    waves = imp.load_source('waves', os.path.join(os.path.dirname(os.path.realpath(__file__)), 'src', 'waves', '__init__.py'))
    try:
        _version = waves.__version__
        _version_detail = waves.__version_detail__
        _dist_name = waves.__name__
    except ImportError:
        _version = None
        _version_detail = None
        _dist_name = None
    return _version, _version_detail, _dist_name

version, version_detail, sdist_name = get_version(mod_root)

setup(
    name='waves-webapp',
    version=version,
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/lirmm/waves-webapp',
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
    namespace_packages=['waves_addons', 'waves_addons.adaptors', 'waves_addons.importers'],
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
