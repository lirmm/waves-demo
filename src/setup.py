from distutils.core import setup

setup(
    name='waves',
    version='1.0',
    packages=['waves', 'waves.api', 'waves.api.views', 'waves.api.serializers', 'waves.api.authentication', 'waves.eav',
              'waves.admin', 'waves.forms', 'waves.forms.admin', 'waves.tests', 'waves.tests.utils', 'waves.utils',
              'waves.views', 'waves.views.admin', 'waves.models', 'waves.runners', 'waves.runners.lib',
              'waves.runners.importer', 'waves.accounts', 'waves.commands', 'waves.managers', 'waves.profiles',
              'waves.exceptions', 'waves.migrations', 'waves_services', 'waves_services.settings'],
    package_dir={'': 'src'},
    url='waves.atgc-montpellier.fr',
    license='MIT',
    author='Marc Chakiachvili, '
           'Floréal Cabanattes, '
           'Vincent Lefort, '
           'Vincent Berry, '
           'Anne-Muriel Arigon Chifolleau',
    author_email='marc.chakiachvili@lirmm.fr, '
                 'floreal.cabanettes@lirmm.fr, '
                 'vincent.lefort@lirmm.fr, '
                 'vincent.berryr@lirmm.fr, '
                 'anne-muriel.arigon@lirmm.fr',
    description='WAVES - Web Application for Versatile Evolutionary bioinformatic Services'
)
