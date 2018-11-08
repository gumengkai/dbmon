# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LinuxRate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('host', models.CharField(max_length=255)),
                ('tags', models.CharField(max_length=255)),
                ('cpu_decute', models.IntegerField()),
                ('mem_decute', models.IntegerField()),
                ('linux_rate', models.IntegerField()),
                ('linux_rate_level', models.CharField(max_length=255)),
                ('linux_rate_color', models.CharField(max_length=255)),
                ('linux_rate_reason', models.CharField(max_length=255)),
                ('rate_time', models.DateTimeField()),
            ],
            options={
                'db_table': 'linux_rate',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='LinuxRateHis',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('host', models.CharField(max_length=255)),
                ('tags', models.CharField(max_length=255)),
                ('cpu_decute', models.IntegerField()),
                ('mem_decute', models.IntegerField()),
                ('linux_rate', models.IntegerField()),
                ('linux_rate_level', models.CharField(max_length=255)),
                ('linux_rate_color', models.CharField(max_length=255)),
                ('linux_rate_reason', models.CharField(max_length=255)),
                ('rate_time', models.DateTimeField()),
            ],
            options={
                'db_table': 'linux_rate_his',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='OsFilesystem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tags', models.CharField(max_length=255)),
                ('host', models.CharField(max_length=255)),
                ('host_name', models.CharField(max_length=255)),
                ('filesystem_name', models.CharField(max_length=255)),
                ('size', models.CharField(max_length=255)),
                ('avail', models.CharField(max_length=255)),
                ('pct_used', models.FloatField()),
                ('disk_rate_level', models.CharField(max_length=255)),
                ('chk_time', models.DateTimeField()),
            ],
            options={
                'db_table': 'os_filesystem',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='OsFilesystemHis',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tags', models.CharField(max_length=255)),
                ('host', models.CharField(max_length=255)),
                ('host_name', models.CharField(max_length=255)),
                ('filesystem_name', models.CharField(max_length=255)),
                ('size', models.CharField(max_length=255)),
                ('avail', models.CharField(max_length=255)),
                ('pct_used', models.FloatField()),
                ('disk_rate_level', models.CharField(max_length=255)),
                ('chk_time', models.DateTimeField()),
            ],
            options={
                'db_table': 'os_filesystem_his',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='OsInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tags', models.CharField(max_length=255)),
                ('host', models.CharField(max_length=255)),
                ('host_name', models.CharField(max_length=255)),
                ('recv_kbps', models.FloatField(null=True, blank=True)),
                ('send_kbps', models.FloatField(null=True, blank=True)),
                ('cpu_used', models.FloatField(null=True, blank=True)),
                ('cpu_rate_level', models.CharField(max_length=255, null=True, blank=True)),
                ('mem_used', models.FloatField(null=True, blank=True)),
                ('mem_rate_level', models.CharField(max_length=255, null=True, blank=True)),
                ('mon_status', models.CharField(max_length=255)),
                ('rate_level', models.CharField(max_length=255)),
                ('chk_time', models.DateTimeField()),
            ],
            options={
                'db_table': 'os_info',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='OsInfoHis',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tags', models.CharField(max_length=255)),
                ('host', models.CharField(max_length=255)),
                ('host_name', models.CharField(max_length=255)),
                ('recv_kbps', models.FloatField(null=True, blank=True)),
                ('send_kbps', models.FloatField(null=True, blank=True)),
                ('cpu_used', models.FloatField(null=True, blank=True)),
                ('cpu_rate_level', models.CharField(max_length=255, null=True, blank=True)),
                ('mem_used', models.FloatField(null=True, blank=True)),
                ('mem_rate_level', models.CharField(max_length=255, null=True, blank=True)),
                ('mon_status', models.CharField(max_length=255)),
                ('rate_level', models.CharField(max_length=255)),
                ('chk_time', models.DateTimeField()),
            ],
            options={
                'db_table': 'os_info_his',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='TabLinuxServers',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tags', models.CharField(max_length=255)),
                ('host', models.CharField(max_length=255)),
                ('host_name', models.CharField(max_length=255)),
                ('user', models.CharField(max_length=255)),
                ('password', models.CharField(max_length=255)),
                ('connect', models.CharField(max_length=255)),
                ('connect_cn', models.CharField(max_length=255, null=True, blank=True)),
                ('cpu', models.CharField(max_length=255)),
                ('cpu_cn', models.CharField(max_length=255, null=True, blank=True)),
                ('mem', models.CharField(max_length=255)),
                ('mem_cn', models.CharField(max_length=255, null=True, blank=True)),
                ('disk', models.CharField(max_length=255)),
                ('disk_cn', models.CharField(max_length=255, null=True, blank=True)),
            ],
            options={
                'db_table': 'tab_linux_servers',
                'managed': False,
            },
        ),
    ]
