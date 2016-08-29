from __future__ import unicode_literals

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Dump all WAVES configuration setup'

    def handle(self, *args, **options):
        import waves.settings
        from django.conf import settings
        var_dict = vars(waves.settings)
        self.stdout.write("*******************************")
        self.stdout.write("****  WAVES current setup *****")
        self.stdout.write("*******************************")
        self.stdout.write('Current Django default database: %s' % settings.DATABASES['default'])
        self.stdout.write('Current Django media root: %s' % settings.MEDIA_ROOT)
        self.stdout.write('Current Django media static dirs: %s' % settings.STATICFILES_DIRS)
        self.stdout.write('Current Django media static root: %s' % settings.STATIC_ROOT)
        self.stdout.write('Current Django allowed hosts: %s' % settings.ALLOWED_HOSTS)
        self.stdout.write("*******************************")
        for key in sorted(var_dict.keys()):
            if key.startswith('WAVES'):
                self.stdout.write('%s: %s' % (key, var_dict[key]))
        self.stdout.write("*******************************")
