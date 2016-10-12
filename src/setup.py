from distutils.core import setup

setup(
    name='waves-webapp',
    version='0.1.0-beta',
    packages=['waves', 'waves.api', 'waves.api.views', 'waves.api.serializers', 'waves.api.authentication',
              'waves.urls', 'waves.admin', 'waves.const', 'waves.forms', 'waves.forms.lib', 'waves.forms.admin',
              'waves.forms.exceptions', 'waves.tests', 'waves.tests.utils', 'waves.utils', 'waves.views',
              'waves.views.admin', 'waves.models', 'waves.accounts', 'waves.adaptors', 'waves.adaptors.api',
              'waves.adaptors.importer', 'waves.commands', 'waves.managers', 'waves.profiles', 'waves.exceptions',
              'waves.management', 'waves.management.commands', 'waves.migrations', 'waves.templatetags',
              'waves_services', 'waves_services.settings'],
    package_dir={'': 'src'},
    url='http://waves.atgc-montpellier.fr',
    license='GNU GPLV3',
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
    description='Web Application for Versatile and Easy BioInformatics Services'
)
