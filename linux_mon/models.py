from django.db import models

# Create your models here.

class OsFilesystem(models.Model):
    tags = models.CharField(max_length=255)
    host = models.CharField(max_length=255)
    host_name = models.CharField(max_length=255)
    filesystem_name = models.CharField(max_length=255)
    size = models.CharField(max_length=255)
    avail = models.CharField(max_length=255)
    pct_used = models.FloatField()
    disk_rate_level = models.CharField(max_length=255)
    chk_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'os_filesystem'


class OsFilesystemHis(models.Model):
    tags = models.CharField(max_length=255)
    host = models.CharField(max_length=255)
    host_name = models.CharField(max_length=255)
    filesystem_name = models.CharField(max_length=255)
    size = models.CharField(max_length=255)
    avail = models.CharField(max_length=255)
    pct_used = models.FloatField()
    disk_rate_level = models.CharField(max_length=255)
    chk_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'os_filesystem_his'


class OsInfo(models.Model):
    tags = models.CharField(max_length=255)
    host = models.CharField(max_length=255)
    host_name = models.CharField(max_length=255)
    updays = models.FloatField(blank=True, null=True)
    recv_kbps = models.FloatField(blank=True, null=True)
    send_kbps = models.FloatField(blank=True, null=True)
    load1 = models.FloatField(blank=True, null=True)
    load5 = models.FloatField(blank=True, null=True)
    load15 = models.FloatField(blank=True, null=True)
    cpu_sys = models.FloatField(blank=True, null=True)
    cpu_iowait = models.FloatField(blank=True, null=True)
    cpu_user = models.FloatField(blank=True, null=True)
    cpu_used = models.FloatField(blank=True, null=True)
    cpu_rate_level = models.CharField(max_length=255, blank=True, null=True)
    mem_used = models.FloatField(blank=True, null=True)
    mem_rate_level = models.CharField(max_length=255, blank=True, null=True)
    tcp_close = models.FloatField(blank=True, null=True)
    tcp_timewait = models.FloatField(blank=True, null=True)
    tcp_connected = models.FloatField(blank=True, null=True)
    tcp_syn = models.FloatField(blank=True, null=True)
    tcp_listen = models.FloatField(blank=True, null=True)
    mon_status = models.CharField(max_length=255)
    rate_level = models.CharField(max_length=255)
    chk_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'os_info'


class OsInfoHis(models.Model):
    tags = models.CharField(max_length=255)
    host = models.CharField(max_length=255)
    host_name = models.CharField(max_length=255)
    updays = models.FloatField(blank=True, null=True)
    recv_kbps = models.FloatField(blank=True, null=True)
    send_kbps = models.FloatField(blank=True, null=True)
    load1 = models.FloatField(blank=True, null=True)
    load5 = models.FloatField(blank=True, null=True)
    load15 = models.FloatField(blank=True, null=True)
    cpu_sys = models.FloatField(blank=True, null=True)
    cpu_iowait = models.FloatField(blank=True, null=True)
    cpu_user = models.FloatField(blank=True, null=True)
    cpu_used = models.FloatField(blank=True, null=True)
    cpu_rate_level = models.CharField(max_length=255, blank=True, null=True)
    mem_used = models.FloatField(blank=True, null=True)
    mem_rate_level = models.CharField(max_length=255, blank=True, null=True)
    tcp_close = models.FloatField(blank=True, null=True)
    tcp_timewait = models.FloatField(blank=True, null=True)
    tcp_connected = models.FloatField(blank=True, null=True)
    tcp_syn = models.FloatField(blank=True, null=True)
    tcp_listen = models.FloatField(blank=True, null=True)
    mon_status = models.CharField(max_length=255)
    rate_level = models.CharField(max_length=255)
    chk_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'os_info_his'

class TabLinuxServers(models.Model):
    tags = models.CharField(max_length=255)
    host = models.CharField(max_length=255)
    host_name = models.CharField(max_length=255)
    user = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    connect = models.CharField(max_length=255)
    connect_cn = models.CharField(max_length=255, blank=True, null=True)
    cpu = models.CharField(max_length=255)
    cpu_cn = models.CharField(max_length=255, blank=True, null=True)
    mem = models.CharField(max_length=255)
    mem_cn = models.CharField(max_length=255, blank=True, null=True)
    disk = models.CharField(max_length=255)
    disk_cn = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tab_linux_servers'


class LinuxRate(models.Model):
    host = models.CharField(max_length=255)
    tags = models.CharField(max_length=255)
    cpu_decute = models.IntegerField()
    mem_decute = models.IntegerField()
    linux_rate = models.IntegerField()
    linux_rate_level = models.CharField(max_length=255)
    linux_rate_color = models.CharField(max_length=255)
    linux_rate_reason = models.CharField(max_length=255)
    rate_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'linux_rate'

class LinuxRateHis(models.Model):
    host = models.CharField(max_length=255)
    tags = models.CharField(max_length=255)
    cpu_decute = models.IntegerField()
    mem_decute = models.IntegerField()
    linux_rate = models.IntegerField()
    linux_rate_level = models.CharField(max_length=255)
    linux_rate_color = models.CharField(max_length=255)
    linux_rate_reason = models.CharField(max_length=255)
    rate_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'linux_rate_his'
