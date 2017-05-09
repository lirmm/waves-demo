# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-09 11:55
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager
import mptt.fields
import polymorphic_tree.models
import uuid
import waves.compat
import waves.models.adaptors
import waves.models.base
import waves.models.inputs
import waves.utils.storage
import waves.utils.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AdaptorInitParam',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, help_text='Param name', max_length=100, null=True, verbose_name='Name')),
                ('value', models.CharField(blank=True, help_text='Default value', max_length=500, null=True, verbose_name='Value')),
                ('crypt', models.BooleanField(default=False, editable=False, verbose_name='Encrypted')),
                ('prevent_override', models.BooleanField(default=False, help_text='Prevent override', verbose_name='Prevent override')),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'Initial param',
                'verbose_name_plural': 'Init params',
            },
        ),
        migrations.CreateModel(
            name='AParam',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('api_name', models.CharField(blank=True, help_text='Api short code, must be unique', max_length=100, null=True)),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Ordering in forms')),
                ('label', models.CharField(help_text='Input displayed label', max_length=100, verbose_name='Label')),
                ('name', models.CharField(help_text="Input runner's job param command line name", max_length=50, verbose_name='Parameter name')),
                ('multiple', models.BooleanField(default=False, help_text='Can hold multiple values', verbose_name='Multiple')),
                ('help_text', models.TextField(blank=True, null=True, verbose_name='Help Text')),
                ('required', models.NullBooleanField(choices=[(True, 'Required'), (None, 'Not submitted'), (False, 'Optional')], default=True, help_text='Submitted and/or Required', verbose_name='Required')),
                ('default', models.CharField(blank=True, max_length=50, null=True, verbose_name='Default value')),
                ('cmd_format', models.IntegerField(choices=[(0, 'Not used'), (2, '-[name] value'), (1, '--[name]=value'), (3, '-[name]'), (5, '--[name]'), (4, 'Posix')], default=2, help_text='Command line pattern', verbose_name='Command line format')),
                ('edam_formats', models.CharField(blank=True, help_text='comma separated list of supported edam format', max_length=255, null=True, verbose_name='Edam format(s)')),
                ('edam_datas', models.CharField(blank=True, help_text='comma separated list of supported edam data type', max_length=255, null=True, verbose_name='Edam data(s)')),
                ('when_value', models.CharField(blank=True, help_text='Input is treated only for this parent value', max_length=255, null=True, verbose_name='When value')),
                ('regexp', models.CharField(blank=True, max_length=255, null=True, verbose_name='Validation Regexp')),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
            ],
            options={
                'ordering': ['order'],
                'verbose_name': 'Param',
                'verbose_name_plural': 'Params',
            },
        ),
        migrations.CreateModel(
            name='FileInputSample',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=255, null=True, verbose_name='Input Label')),
                ('help_text', models.CharField(blank=True, max_length=255, null=True, verbose_name='Help text')),
                ('file', models.FileField(storage=waves.utils.storage.WavesStorage(), upload_to=waves.utils.storage.file_sample_directory, verbose_name='Sample file')),
            ],
            options={
                'verbose_name': 'Input sample',
                'verbose_name_plural': 'Input samples',
            },
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, help_text='Creation timestamp', verbose_name='Created on')),
                ('updated', models.DateTimeField(auto_now=True, help_text='Last update timestamp', verbose_name='Last Update')),
                ('slug', models.UUIDField(blank=True, default=uuid.uuid4, editable=False, unique=True)),
                ('title', models.CharField(blank=True, max_length=255, null=True, verbose_name='Job title')),
                ('status', models.IntegerField(choices=[(-1, 'Undefined'), (0, 'Created'), (1, 'Prepared'), (2, 'Queued'), (3, 'Running'), (4, 'Suspended'), (5, 'Run completed'), (6, 'Completed'), (7, 'Cancelled'), (9, 'Error')], default=0, help_text='Job current run status', verbose_name='Job status')),
                ('status_mail', models.IntegerField(default=9999, editable=False)),
                ('email_to', models.EmailField(blank=True, help_text='Notify results to this email', max_length=254, null=True, verbose_name='Email results')),
                ('exit_code', models.IntegerField(default=0, help_text='Job exit code on relative adaptor', verbose_name='Job system exit code')),
                ('results_available', models.BooleanField(default=False, editable=False, verbose_name='Results are available')),
                ('nb_retry', models.IntegerField(default=0, editable=False, verbose_name='Nb Retry')),
                ('remote_job_id', models.CharField(editable=False, max_length=255, null=True, verbose_name='Remote job ID')),
                ('remote_history_id', models.CharField(editable=False, max_length=255, null=True, verbose_name='Remote history ID')),
                ('client', models.ForeignKey(blank=True, help_text='Associated registered user', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='clients_job', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-updated', '-created'],
                'abstract': False,
                'db_table': 'waves_job',
                'verbose_name': 'Job',
            },
            bases=(models.Model, waves.models.base.UrlMixin, waves.models.adaptors.DTOMixin),
        ),
        migrations.CreateModel(
            name='JobHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True, help_text=b'History timestamp', verbose_name=b'Date time')),
                ('status', models.IntegerField(choices=[(-1, 'Undefined'), (0, 'Created'), (1, 'Prepared'), (2, 'Queued'), (3, 'Running'), (4, 'Suspended'), (5, 'Run completed'), (6, 'Completed'), (7, 'Cancelled'), (9, 'Error')], help_text=b'History job status', null=True, verbose_name=b'Job Status')),
                ('message', models.TextField(blank=True, help_text=b'History log', null=True, verbose_name=b'History log')),
                ('is_admin', models.BooleanField(default=False, verbose_name=b'Admin Message')),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='job_history', to='waves.Job')),
            ],
            options={
                'ordering': ['-timestamp', '-status'],
                'db_table': 'waves_job_history',
            },
        ),
        migrations.CreateModel(
            name='JobInput',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(default=0)),
                ('slug', models.UUIDField(blank=True, default=uuid.uuid4, editable=False, unique=True)),
                ('api_name', models.CharField(blank=True, help_text='Api short code, must be unique', max_length=100, null=True)),
                ('value', models.CharField(blank=True, help_text='Input value (filename, boolean value, int value etc.)', max_length=255, null=True, verbose_name='Input content')),
                ('remote_input_id', models.CharField(editable=False, max_length=255, null=True, verbose_name='Remote input ID (on adaptor)')),
                ('type', models.CharField(choices=[('file', 'Input file'), ('list', 'List of values'), ('boolean', 'Boolean'), ('decimal', 'Decimal'), ('int', 'Integer'), ('text', 'Text')], editable=False, max_length=50, null=True, verbose_name='Param type')),
                ('name', models.CharField(editable=False, max_length=200, null=True, verbose_name='Param name')),
                ('param_type', models.IntegerField(choices=[(0, 'Not used'), (2, '-[name] value'), (1, '--[name]=value'), (3, '-[name]'), (5, '--[name]'), (4, 'Posix')], default=0, editable=False, null=True, verbose_name='Parameter Type')),
                ('label', models.CharField(editable=False, max_length=100, null=True, verbose_name='Label')),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='job_inputs', to='waves.Job')),
            ],
            options={
                'db_table': 'waves_job_input',
            },
        ),
        migrations.CreateModel(
            name='JobOutput',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(default=0)),
                ('slug', models.UUIDField(blank=True, default=uuid.uuid4, editable=False, unique=True)),
                ('api_name', models.CharField(blank=True, help_text='Api short code, must be unique', max_length=100, null=True)),
                ('value', models.CharField(blank=True, default='', max_length=200, null=True, verbose_name='Output value')),
                ('remote_output_id', models.CharField(editable=False, max_length=255, null=True, verbose_name='Remote output ID (on adaptor)')),
                ('_name', models.CharField(help_text='Output displayed name', max_length=200, verbose_name='Name')),
                ('type', models.CharField(default='.txt', max_length=5, verbose_name='File extension')),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='outputs', to='waves.Job')),
            ],
            options={
                'db_table': 'waves_job_output',
            },
            bases=(waves.models.base.UrlMixin, models.Model),
        ),
        migrations.CreateModel(
            name='RepeatedGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(default=0)),
                ('name', models.CharField(max_length=255, verbose_name='Group name')),
                ('title', models.CharField(max_length=255, verbose_name='Group title')),
                ('max_repeat', models.IntegerField(blank=True, null=True, verbose_name='Max repeat')),
                ('min_repeat', models.IntegerField(default=0, verbose_name='Min repeat')),
                ('default', models.IntegerField(default=0, verbose_name='Default repeat')),
            ],
            options={
                'db_table': 'waves_repeat_group',
            },
            bases=(waves.models.adaptors.DTOMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Runner',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', waves.compat.RichTextField(blank=True, help_text='Description (HTML)', null=True, verbose_name='Description')),
                ('short_description', models.TextField(blank=True, help_text='Short description (Text)', null=True, verbose_name='Short Description')),
                ('clazz', models.CharField(help_text='This is the concrete class used to perform job execution', max_length=100, verbose_name='Adaptor object')),
                ('name', models.CharField(help_text='Displayed name', max_length=50, verbose_name='Label')),
                ('importer_clazz', models.CharField(blank=True, max_length=200, null=True, verbose_name='Importer')),
            ],
            options={
                'ordering': ['name'],
                'db_table': 'waves_runner',
                'verbose_name': 'Execution',
                'verbose_name_plural': 'Execution',
            },
            bases=(waves.models.base.ExportAbleMixin, models.Model),
        ),
        migrations.CreateModel(
            name='SampleDepParam',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('set_default', models.CharField(max_length=200, verbose_name='Set value to ')),
            ],
            options={
                'db_table': 'waves_sample_dependent_input',
                'verbose_name': 'Sample dependency',
                'verbose_name_plural': 'Sample dependencies',
            },
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, help_text='Creation timestamp', verbose_name='Created on')),
                ('updated', models.DateTimeField(auto_now=True, help_text='Last update timestamp', verbose_name='Last Update')),
                ('description', waves.compat.RichTextField(blank=True, help_text='Description (HTML)', null=True, verbose_name='Description')),
                ('short_description', models.TextField(blank=True, help_text='Short description (Text)', null=True, verbose_name='Short Description')),
                ('api_name', models.CharField(blank=True, help_text='Api short code, must be unique', max_length=100, null=True)),
                ('name', models.CharField(help_text='Service displayed name', max_length=255, verbose_name='Service name')),
                ('version', models.CharField(blank=True, default='1.0', help_text='Service displayed version', max_length=10, null=True, verbose_name='Current version')),
                ('status', models.IntegerField(choices=[[0, 'Draft'], [1, 'Test'], [2, 'Restricted'], [3, 'Public']], default=0, help_text='Service online status')),
                ('api_on', models.BooleanField(default=True, help_text='Service is available for waves_api calls', verbose_name='Available on API')),
                ('web_on', models.BooleanField(default=True, help_text='Service is available for web front', verbose_name='Available on WEB')),
                ('email_on', models.BooleanField(default=True, help_text='This service sends notification email', verbose_name='Notify results')),
                ('partial', models.BooleanField(default=False, help_text='Set whether some service outputs are dynamic (not known in advance)', verbose_name='Dynamic outputs')),
                ('remote_service_id', models.CharField(editable=False, max_length=255, null=True, verbose_name='Remote service tool ID')),
                ('edam_topics', models.TextField(blank=True, help_text='Comma separated list of Edam ontology topics', null=True, verbose_name='Edam topics')),
                ('edam_operations', models.TextField(blank=True, help_text='Comma separated list of Edam ontology operations', null=True, verbose_name='Edam operations')),
            ],
            options={
                'ordering': ['name'],
                'db_table': 'waves_service',
                'verbose_name': 'Service',
            },
            bases=(waves.models.base.ExportAbleMixin, waves.models.adaptors.DTOMixin, models.Model),
        ),
        migrations.CreateModel(
            name='ServiceCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(default=0)),
                ('description', waves.compat.RichTextField(blank=True, help_text='Description (HTML)', null=True, verbose_name='Description')),
                ('short_description', models.TextField(blank=True, help_text='Short description (Text)', null=True, verbose_name='Short Description')),
                ('api_name', models.CharField(blank=True, help_text='Api short code, must be unique', max_length=100, null=True)),
                ('name', models.CharField(help_text='Category name', max_length=255, verbose_name='Category Name')),
                ('ref', models.URLField(blank=True, help_text='Category online reference', null=True, verbose_name='Reference')),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('mptt_level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('parent', mptt.fields.TreeForeignKey(blank=True, help_text='Parent category', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children_category', to='waves.ServiceCategory')),
            ],
            options={
                'ordering': ['name'],
                'verbose_name_plural': 'Categories',
                'db_table': 'waves_service_category',
                'verbose_name': 'Category',
            },
        ),
        migrations.CreateModel(
            name='ServiceMeta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(default=0)),
                ('description', waves.compat.RichTextField(blank=True, help_text='Description (HTML)', null=True, verbose_name='Description')),
                ('short_description', models.TextField(blank=True, help_text='Short description (Text)', null=True, verbose_name='Short Description')),
                ('type', models.CharField(choices=[('cite', 'Citation'), ('cmd', 'Command line'), ('doc', 'Documentation'), ('download', 'Downloads'), ('feat', 'Features'), ('misc', 'Miscellaneous'), ('website', 'Online resources'), ('paper', 'Related Paper'), ('rtfm', 'User Guide')], max_length=100, verbose_name='Meta type')),
                ('title', models.CharField(blank=True, max_length=255, null=True, verbose_name='Title')),
                ('value', models.CharField(blank=True, max_length=500, null=True, verbose_name='Link')),
                ('is_url', models.BooleanField(default=False, editable=False, verbose_name='Is a url')),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='metas', to='waves.Service')),
            ],
            options={
                'db_table': 'waves_service_meta',
                'verbose_name': 'Information',
            },
        ),
        migrations.CreateModel(
            name='Submission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, help_text='Creation timestamp', verbose_name='Created on')),
                ('updated', models.DateTimeField(auto_now=True, help_text='Last update timestamp', verbose_name='Last Update')),
                ('order', models.PositiveIntegerField(default=0)),
                ('slug', models.UUIDField(blank=True, default=uuid.uuid4, editable=False, unique=True)),
                ('api_name', models.CharField(blank=True, help_text='Api short code, must be unique', max_length=100, null=True)),
                ('availability', models.IntegerField(choices=[(0, 'Not Available'), (1, 'Available on web only'), (2, 'Available on waves_api only'), (3, 'Available on both')], default=3, verbose_name='Availability')),
                ('name', models.CharField(max_length=255, verbose_name='Submission title')),
                ('runner', models.ForeignKey(help_text='Service job runs adapter', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='waves_submission_runs', to='waves.Runner')),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submissions', to='waves.Service')),
            ],
            options={
                'ordering': ('order',),
                'verbose_name_plural': 'Submissions',
                'db_table': 'waves_submission',
                'verbose_name': 'Submission',
            },
        ),
        migrations.CreateModel(
            name='SubmissionExitCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('exit_code', models.IntegerField(verbose_name='Exit code value')),
                ('message', models.CharField(max_length=255, verbose_name='Exit code message')),
                ('is_error', models.BooleanField(default=False, verbose_name='Is an Error')),
                ('submission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exit_codes', to='waves.Submission')),
            ],
            options={
                'db_table': 'waves_service_exitcode',
                'verbose_name': 'Exit Code',
            },
        ),
        migrations.CreateModel(
            name='SubmissionOutput',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, help_text='Creation timestamp', verbose_name='Created on')),
                ('updated', models.DateTimeField(auto_now=True, help_text='Last update timestamp', verbose_name='Last Update')),
                ('api_name', models.CharField(blank=True, help_text='Api short code, must be unique', max_length=100, null=True)),
                ('label', models.CharField(help_text='Label', max_length=255, null=True, verbose_name='Label')),
                ('file_pattern', models.CharField(help_text='Pattern is used to match input value (%s to retrieve value from input)', max_length=100, verbose_name='File name or name pattern')),
                ('edam_format', models.CharField(blank=True, help_text='Edam format', max_length=255, null=True, verbose_name='Edam format')),
                ('edam_data', models.CharField(blank=True, help_text='Edam data', max_length=255, null=True, verbose_name='Edam data')),
                ('help_text', models.TextField(blank=True, null=True, verbose_name='Help Text')),
            ],
            options={
                'ordering': ['-created'],
                'db_table': 'waves_submission_output',
                'verbose_name': 'Output',
                'verbose_name_plural': 'Outputs',
            },
        ),
        migrations.CreateModel(
            name='BooleanParam',
            fields=[
                ('aparam_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='waves.AParam')),
                ('true_value', models.CharField(default='True', max_length=50, verbose_name='True value')),
                ('false_value', models.CharField(default='False', max_length=50, verbose_name='False value')),
            ],
            options={
                'verbose_name': 'Boolean choice',
                'verbose_name_plural': 'Boolean choices',
            },
            bases=('waves.aparam',),
            managers=[
                ('objects', django.db.models.manager.Manager()),
                ('base_objects', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='DecimalParam',
            fields=[
                ('aparam_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='waves.AParam')),
                ('min_val', models.DecimalField(blank=True, decimal_places=3, default=None, help_text='Leave blank if no min', max_digits=50, null=True, verbose_name='Min value')),
                ('max_val', models.DecimalField(blank=True, decimal_places=3, default=None, help_text='Leave blank if no max', max_digits=50, null=True, verbose_name='Max value')),
                ('step', models.DecimalField(blank=True, decimal_places=3, default=0.5, max_digits=50, verbose_name='Step')),
            ],
            options={
                'verbose_name': 'Decimal',
                'verbose_name_plural': 'Decimal',
            },
            bases=(waves.models.inputs.NumberParam, 'waves.aparam'),
            managers=[
                ('objects', django.db.models.manager.Manager()),
                ('base_objects', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='FileInput',
            fields=[
                ('aparam_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='waves.AParam')),
                ('max_size', models.BigIntegerField(default=20480, help_text='in Ko', verbose_name='Maximum allowed file size ')),
                ('allowed_extensions', models.CharField(default='*', help_text='Comma separated list, * means no filter', max_length=255, validators=[waves.utils.validators.validate_list_comma], verbose_name='Filter by extensions')),
            ],
            options={
                'ordering': ['order'],
                'db_table': 'waves_service_file',
                'verbose_name': 'File',
                'verbose_name_plural': 'Files input',
            },
            bases=('waves.aparam',),
            managers=[
                ('objects', django.db.models.manager.Manager()),
                ('base_objects', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='IntegerParam',
            fields=[
                ('aparam_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='waves.AParam')),
                ('min_val', models.IntegerField(blank=True, default=0, help_text='Leave blank if no min', null=True, verbose_name='Min value')),
                ('max_val', models.IntegerField(blank=True, default=None, help_text='Leave blank if no max', null=True, verbose_name='Max value')),
                ('step', models.IntegerField(blank=True, default=1, verbose_name='Step')),
            ],
            options={
                'verbose_name': 'Integer',
                'verbose_name_plural': 'Integer',
            },
            bases=(waves.models.inputs.NumberParam, 'waves.aparam'),
            managers=[
                ('objects', django.db.models.manager.Manager()),
                ('base_objects', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='ListParam',
            fields=[
                ('aparam_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='waves.AParam')),
                ('list_mode', models.CharField(choices=[('select', 'Select List'), ('radio', 'Radio buttons'), ('checkbox', 'Check box')], default='select', max_length=100, verbose_name='List display mode')),
                ('list_elements', models.TextField(help_text='One Element per line label|value', max_length=500, validators=[waves.utils.validators.validate_list_param], verbose_name='Elements')),
            ],
            options={
                'verbose_name': 'List',
                'verbose_name_plural': 'Lists',
            },
            bases=('waves.aparam',),
            managers=[
                ('objects', django.db.models.manager.Manager()),
                ('base_objects', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AddField(
            model_name='submissionoutput',
            name='from_input',
            field=models.ForeignKey(blank=True, help_text='Valuated with input', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='to_outputs', to='waves.AParam'),
        ),
        migrations.AddField(
            model_name='submissionoutput',
            name='submission',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='outputs', to='waves.Submission'),
        ),
        migrations.AddField(
            model_name='service',
            name='category',
            field=models.ForeignKey(help_text='Service category', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='category_tools', to='waves.ServiceCategory'),
        ),
        migrations.AddField(
            model_name='service',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='service',
            name='restricted_client',
            field=models.ManyToManyField(blank=True, db_table='waves_service_client', help_text='By default access is granted to everyone, you may restrict access here.', related_name='restricted_services', to=settings.AUTH_USER_MODEL, verbose_name='Restricted clients'),
        ),
        migrations.AddField(
            model_name='service',
            name='runner',
            field=models.ForeignKey(help_text='Service job runs adapter', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='waves_service_runs', to='waves.Runner'),
        ),
        migrations.AddField(
            model_name='sampledepparam',
            name='related_to',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='related_samples', to='waves.AParam'),
        ),
        migrations.AddField(
            model_name='sampledepparam',
            name='sample',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dependent_inputs', to='waves.FileInputSample'),
        ),
        migrations.AddField(
            model_name='repeatedgroup',
            name='submission',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='submission_groups', to='waves.Submission'),
        ),
        migrations.AddField(
            model_name='job',
            name='submission',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='service_jobs', to='waves.Submission'),
        ),
        migrations.AddField(
            model_name='fileinputsample',
            name='dependent_params',
            field=models.ManyToManyField(blank=True, through='waves.SampleDepParam', to='waves.AParam'),
        ),
        migrations.AddField(
            model_name='aparam',
            name='parent',
            field=polymorphic_tree.models.PolymorphicTreeForeignKey(blank=True, help_text='Input is associated to', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='dependents_inputs', to='waves.AParam'),
        ),
        migrations.AddField(
            model_name='aparam',
            name='polymorphic_ctype',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='polymorphic_waves.aparam_set+', to='contenttypes.ContentType'),
        ),
        migrations.AddField(
            model_name='aparam',
            name='repeat_group',
            field=models.ForeignKey(blank=True, help_text='Group and repeat items', null=True, on_delete=django.db.models.deletion.SET_NULL, to='waves.RepeatedGroup'),
        ),
        migrations.AddField(
            model_name='aparam',
            name='submission',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submission_inputs', to='waves.Submission'),
        ),
        migrations.CreateModel(
            name='JobAdminHistory',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('waves.jobhistory',),
        ),
        migrations.CreateModel(
            name='RelatedParam',
            fields=[
            ],
            options={
                'verbose_name': 'Related Param',
                'proxy': True,
                'verbose_name_plural': 'Related params',
                'indexes': [],
            },
            bases=('waves.aparam',),
        ),
        migrations.CreateModel(
            name='ServiceRunParam',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('waves.adaptorinitparam',),
        ),
        migrations.CreateModel(
            name='SubmissionRunParam',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('waves.adaptorinitparam',),
        ),
        migrations.CreateModel(
            name='TextParam',
            fields=[
            ],
            options={
                'verbose_name': 'Text',
                'proxy': True,
                'verbose_name_plural': 'Text',
                'indexes': [],
            },
            bases=('waves.aparam',),
        ),
        migrations.AlterUniqueTogether(
            name='submissionexitcode',
            unique_together=set([('exit_code', 'submission')]),
        ),
        migrations.AlterUniqueTogether(
            name='submission',
            unique_together=set([('service', 'api_name')]),
        ),
        migrations.AlterUniqueTogether(
            name='servicecategory',
            unique_together=set([('api_name',)]),
        ),
        migrations.AlterUniqueTogether(
            name='service',
            unique_together=set([('api_name', 'version', 'status')]),
        ),
        migrations.AddField(
            model_name='sampledepparam',
            name='file_input',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sample_dependencies', to='waves.FileInput'),
        ),
        migrations.AlterUniqueTogether(
            name='joboutput',
            unique_together=set([('_name', 'job')]),
        ),
        migrations.AlterUniqueTogether(
            name='jobinput',
            unique_together=set([('name', 'value', 'job')]),
        ),
        migrations.AlterUniqueTogether(
            name='jobhistory',
            unique_together=set([('job', 'timestamp', 'status', 'is_admin')]),
        ),
        migrations.AddField(
            model_name='fileinputsample',
            name='file_input',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='input_samples', to='waves.FileInput'),
        ),
    ]
