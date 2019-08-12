from __future__ import unicode_literals

from django.db import models

# Create your models here.

class RedisMonConf(models.Model):
    tags = models.CharField(max_length=255)
    host = models.CharField(max_length=255)
    port = models.IntegerField()
    connect = models.CharField(max_length=255)
    mem = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'redis_mon_conf'

class Redis(models.Model):
    host = models.CharField(max_length=255)
    port = models.IntegerField(blank=True, null=False)
    tags = models.CharField(max_length=255)
    version = models.CharField(max_length=255, blank=True, null=True)
    updays = models.IntegerField(blank=True, null=True)
    redis_mode = models.CharField(max_length=255)
    slaves = models.IntegerField(blank=True, null=True)
    connection_clients = models.IntegerField(blank=True, null=True)
    role = models.CharField(max_length=255, blank=True, null=True)
    used_memory = models.FloatField()
    mem_fragmentation_ratio = models.FloatField()
    total_keys = models.IntegerField(blank=True, null=True)
    max_memory = models.FloatField()
    used_memory_pct = models.FloatField()
    misses = models.IntegerField(blank=True, null=True)
    hits = models.IntegerField(blank=True, null=True)
    mon_status = models.CharField(max_length=255)
    rate_level = models.CharField(max_length=255)
    chk_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'redis'