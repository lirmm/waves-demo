# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-31 15:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('waves', '0008_auto_20170130_1605'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submissionoutput',
            name='ext',
            field=models.CharField(max_length=5, null=True, verbose_name='File extension'),
        ),
    ]
