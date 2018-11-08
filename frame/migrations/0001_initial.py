# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EventRecorder',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('event_type', models.CharField(max_length=255)),
                ('event_type_color', models.CharField(max_length=255)),
                ('event_section', models.CharField(max_length=255)),
                ('event_content', models.TextField()),
                ('record_time', models.DateTimeField()),
            ],
            options={
                'db_table': 'event_recorder',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='TabAlarmConf',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('db_type', models.CharField(max_length=255)),
                ('alarm_name', models.CharField(max_length=255)),
                ('pct_max', models.CharField(max_length=255, null=True, blank=True)),
                ('size_min', models.CharField(max_length=255, null=True, blank=True)),
                ('time_max', models.CharField(max_length=255, null=True, blank=True)),
            ],
            options={
                'db_table': 'tab_alarm_conf',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='TabAlarmEmailInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tags', models.CharField(max_length=255)),
                ('url', models.CharField(max_length=255)),
                ('alarm_type', models.CharField(max_length=255)),
                ('email_header', models.CharField(max_length=255)),
                ('email_content', models.TextField()),
                ('alarm_time', models.DateTimeField()),
            ],
            options={
                'db_table': 'tab_alarm_email_info',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='TabAlarmInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tags', models.CharField(max_length=255)),
                ('url', models.CharField(max_length=255)),
                ('alarm_type', models.CharField(max_length=255)),
                ('alarm_header', models.CharField(max_length=255)),
                ('alarm_content', models.TextField()),
                ('alarm_time', models.DateTimeField()),
            ],
            options={
                'db_table': 'tab_alarm_info',
                'managed': False,
            },
        ),
    ]
