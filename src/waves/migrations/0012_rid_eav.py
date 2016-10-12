# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-10-12 12:16
from __future__ import unicode_literals

from django.db import migrations, models


def migrate_eav_values(apps, schema_editor):

    try:
        from django.conf import settings
        from django.contrib.contenttypes.models import ContentType
        if 'eav' in settings.INSTALLED_APPS:
            import eav
            Job = apps.get_model('waves', 'Job')
            JobInput = apps.get_model('waves', 'JobInput')
            JobOutput = apps.get_model('waves', 'JobOutput')
            eav.register(Job)
            eav.register(JobInput)
            eav.register(JobOutput)

            for job in Job.objects.all():
                # for all existing job migrate data from eav to objects
                job.remote_history_id = job.eav.galaxy_history_id
                for input_job in job.job_inputs.all():
                    input_job.remote_input_id = input_job.eav.galaxy_input_dataset_id
                    input_job.save()
                for output_job in job.job_outputs.all():
                    output_job.remote_output_id = output_job.eav.galaxy_output_dataset_id
                    output_job.save()
                job.save()
        else:
            pass
            # Nothing to do, migration doesn't need to be applied

        # List of deleted apps
        DEL_APPS = ["eav"]
        ct = ContentType.objects.all().order_by("app_label", "model")

        for c in ct:
            if (c.app_label in DEL_APPS):
                print "Deleting Content Type %s %s" % (c.app_label, c.model)
                c.delete()

    except ImportError:
        pass


def reverse_migrate_eav(apps, schema_editor):
    # Nothing to do because we only add new data in other function
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('waves', '0011_add_web_on_service'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='wavessite',
            options={'verbose_name': 'WAVES configuration'},
        ),
        migrations.AddField(
            model_name='job',
            name='remote_history_id',
            field=models.CharField(editable=False, max_length=255, null=True, verbose_name='Remote history ID (on adaptor)'),
        ),
        migrations.AddField(
            model_name='jobinput',
            name='remote_input_id',
            field=models.CharField(editable=False, max_length=255, null=True, verbose_name='Remote input ID (on adaptor)'),
        ),
        migrations.AddField(
            model_name='joboutput',
            name='remote_output_id',
            field=models.CharField(editable=False, max_length=255, null=True, verbose_name='Remote output ID (on adaptor)'),
        ),
        migrations.AlterField(
            model_name='job',
            name='remote_job_id',
            field=models.CharField(editable=False, max_length=255, null=True, verbose_name='Remote job ID (on adaptor)'),
        ),
        migrations.AlterField(
            model_name='wavessite',
            name='theme',
            field=models.CharField(choices=[(b'default', b'Default'), (b'amelia', b'Amelia'), (b'cerulean', b'Cerulean'), (b'cosmo', b'Cosmo'), (b'cyborg', b'Cyborg'), (b'flatly', b'Flatly'), (b'journal', b'Journal'), (b'readable', b'Readable'), (b'simplex', b'Simplex'), (b'slate', b'Slate'), (b'spacelab', b'SpaceLab'), (b'united', b'United'), (b'superhero', b'Superhero'), (b'lumen', b'Lumen')], default='flatly', max_length=255, verbose_name='Bootstrap theme'),
        ),
        migrations.RunPython(migrate_eav_values, reverse_migrate_eav)
    ]
