# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import chunked_uploads.models
from django.conf import settings
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ApiAccess',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('identifier', models.CharField(max_length=255)),
                ('url', models.CharField(default=b'', max_length=255, blank=True)),
                ('request_method', models.CharField(default=b'', max_length=10, blank=True)),
                ('accessed', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='ApiKey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(default=b'', max_length=256, blank=True)),
                ('created', models.DateTimeField(default=datetime.datetime.now)),
                ('user', models.OneToOneField(related_name='chunked_upload_api_key', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Chunk',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('chunk', models.FileField(upload_to=chunked_uploads.models.get_chunks_storage_path)),
                ('chunk_size', models.IntegerField()),
                ('created_at', models.DateTimeField(default=datetime.datetime.now)),
            ],
        ),
        migrations.CreateModel(
            name='Upload',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uuid', django_extensions.db.fields.UUIDField(unique=True, editable=False, blank=True)),
                ('filename', models.CharField(max_length=250)),
                ('filesize', models.IntegerField()),
                ('upload', models.FileField(max_length=250, upload_to=chunked_uploads.models.get_storage_path)),
                ('md5', models.CharField(max_length=32, blank=True)),
                ('state', models.IntegerField(default=1, choices=[(1, b'Uploading'), (2, b'Complete - Chunks Uploaded')])),
                ('created_at', models.DateTimeField(default=datetime.datetime.now)),
                ('user', models.ForeignKey(related_name='uploads', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='chunk',
            name='upload',
            field=models.ForeignKey(related_name='chunks', to='chunked_uploads.Upload'),
        ),
    ]
