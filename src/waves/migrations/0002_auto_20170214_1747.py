# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-14 16:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('waves', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='service',
            name='cmd_parser',
        ),
        migrations.AlterField(
            model_name='service',
            name='api_on',
            field=models.BooleanField(default=True, help_text='Service is available for waves_api calls', verbose_name='Available on API'),
        ),
        migrations.AlterField(
            model_name='submission',
            name='availability',
            field=models.IntegerField(choices=[(0, 'Not Available'), (1, 'Available on web only'), (2, 'Available on waves_api only'), (3, 'Available on both')], default=3, verbose_name='Availability'),
        ),
        migrations.AlterField(
            model_name='wavessiteconfig',
            name='maintenance',
            field=models.BooleanField(default=False, help_text='Redirect everything to 503', verbose_name='Site Maintenance'),
        ),
    ]
