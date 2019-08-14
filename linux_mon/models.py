from django.db import models

# Create your models here.

class OsFilesystem(models.Model):
    tags = models.CharField(max_length=255)
    host = models.CharField(max_length=255)
    host_name = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    size = models.CharField(max_length=255)
    avail = models.CharField(max_length=255)
    pct_used = models.FloatField()
    filesystem = models.CharField(max_length=255)
    disk_rate_level = models.CharField(max_length=255)
    chk_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'os_filesystem'


class OsFilesystemHis(models.Model):
    tags = models.CharField(max_length=255)
    host = models.CharField(max_length=255)
    host_name = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    size = models.CharField(max_length=255)
    avail = models.CharField(max_length=255)
    pct_used = models.FloatField()
    filesystem = models.CharField(max_length=255)
    disk_rate_level = models.CharField(max_length=255)
    chk_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'os_filesystem_his'


class OsInfo(models.Model):
    tags = models.CharField(max_length=255)
    host = models.CharField(max_length=255)
    ssh_port = models.IntegerField()
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
    mem_cache = models.FloatField(blank=True, null=True)
    mem_buffer = models.FloatField(blank=True, null=True)
    mem_free = models.FloatField(blank=True, null=True)
    mem_used_mb = models.FloatField(blank=True, null=True)
    swap_used = models.FloatField(blank=True, null=True)
    swap_free = models.FloatField(blank=True, null=True)
    pgin = models.FloatField(blank=True, null=True)
    pgout = models.FloatField(blank=True, null=True)
    swapin = models.FloatField(blank=True, null=True)
    swapout = models.FloatField(blank=True, null=True)
    pgfault = models.FloatField(blank=True, null=True)
    pgmajfault = models.FloatField(blank=True, null=True)
    mem_rate_level = models.CharField(max_length=255, blank=True, null=True)
    tcp_close = models.FloatField(blank=True, null=True)
    tcp_timewait = models.FloatField(blank=True, null=True)
    tcp_connected = models.FloatField(blank=True, null=True)
    tcp_syn = models.FloatField(blank=True, null=True)
    tcp_listen = models.FloatField(blank=True, null=True)
    iops = models.FloatField(blank=True, null=True)
    read_mb = models.FloatField(blank=True, null=True)
    write_mb = models.FloatField(blank=True, null=True)
    proc_new = models.FloatField(blank=True, null=True)
    proc_running = models.FloatField(blank=True, null=True)
    proc_block = models.FloatField(blank=True, null=True)
    intr = models.FloatField(blank=True, null=True)
    ctx = models.FloatField(blank=True, null=True)
    softirq = models.FloatField(blank=True, null=True)
    hostname = models.CharField(max_length=255)
    ostype = models.CharField(max_length=255)
    kernel = models.CharField(max_length=255)
    frame = models.CharField(max_length=255)
    linux_version = models.CharField(max_length=255)
    cpu_mode = models.CharField(max_length=255)
    cpu_cache = models.CharField(max_length=255)
    processor = models.CharField(max_length=255)
    virtual_cnt = models.IntegerField()
    cpu_speed = models.CharField(max_length=255)
    Memtotal = models.FloatField(blank=True, null=True)
    ipinfo = models.CharField(max_length=255)
    mon_status = models.CharField(max_length=255)
    rate_level = models.CharField(max_length=255)
    chk_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'os_info'


class OsInfoHis(models.Model):
    tags = models.CharField(max_length=255)
    host = models.CharField(max_length=255)
    ssh_port = models.IntegerField()
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
    mem_cache = models.FloatField(blank=True, null=True)
    mem_buffer = models.FloatField(blank=True, null=True)
    mem_free = models.FloatField(blank=True, null=True)
    mem_used_mb = models.FloatField(blank=True, null=True)
    swap_used = models.FloatField(blank=True, null=True)
    swap_free = models.FloatField(blank=True, null=True)
    pgin = models.FloatField(blank=True, null=True)
    pgout = models.FloatField(blank=True, null=True)
    swapin = models.FloatField(blank=True, null=True)
    swapout = models.FloatField(blank=True, null=True)
    pgfault = models.FloatField(blank=True, null=True)
    pgmajfault = models.FloatField(blank=True, null=True)
    mem_rate_level = models.CharField(max_length=255, blank=True, null=True)
    tcp_close = models.FloatField(blank=True, null=True)
    tcp_timewait = models.FloatField(blank=True, null=True)
    tcp_connected = models.FloatField(blank=True, null=True)
    tcp_syn = models.FloatField(blank=True, null=True)
    tcp_listen = models.FloatField(blank=True, null=True)
    iops = models.FloatField(blank=True, null=True)
    read_mb = models.FloatField(blank=True, null=True)
    write_mb = models.FloatField(blank=True, null=True)
    proc_new = models.FloatField(blank=True, null=True)
    proc_running = models.FloatField(blank=True, null=True)
    proc_block = models.FloatField(blank=True, null=True)
    intr = models.FloatField(blank=True, null=True)
    ctx = models.FloatField(blank=True, null=True)
    softirq = models.FloatField(blank=True, null=True)
    hostname = models.CharField(max_length=255)
    ostype = models.CharField(max_length=255)
    kernel = models.CharField(max_length=255)
    frame = models.CharField(max_length=255)
    linux_version = models.CharField(max_length=255)
    cpu_mode = models.CharField(max_length=255)
    cpu_cache = models.CharField(max_length=255)
    processor = models.CharField(max_length=255)
    virtual_cnt = models.IntegerField()
    cpu_speed = models.CharField(max_length=255)
    Memtotal = models.FloatField(blank=True, null=True)
    ipinfo = models.CharField(max_length=255)
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
    ssh_port = models.IntegerField()
    connect = models.CharField(max_length=255)
    cpu = models.CharField(max_length=255)
    mem = models.CharField(max_length=255)
    swap = models.CharField(max_length=255)
    disk = models.CharField(max_length=255)

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

class LinuxIoStat(models.Model):
    tags = models.CharField(max_length=255)
    host = models.CharField(max_length=255)
    disk = models.CharField(max_length=255)
    rd_s = models.FloatField(blank=True, null=True)
    rd_avgkb = models.FloatField(blank=True, null=True)
    rd_m_s = models.FloatField(blank=True, null=True)
    rd_mrg_s = models.FloatField(blank=True, null=True)
    rd_cnc = models.FloatField(blank=True, null=True)
    rd_rt = models.FloatField(blank=True, null=True)
    wr_s = models.FloatField(blank=True, null=True)
    wr_avgkb = models.FloatField(blank=True, null=True)
    wr_m_s = models.FloatField(blank=True, null=True)
    wr_mrg_s = models.FloatField(blank=True, null=True)
    wr_cnc = models.FloatField(blank=True, null=True)
    wr_rt = models.FloatField(blank=True, null=True)
    busy = models.FloatField(blank=True, null=True)
    in_prg = models.FloatField(blank=True, null=True)
    io_s = models.FloatField(blank=True, null=True)
    qtime = models.FloatField(blank=True, null=True)
    stime = models.FloatField(blank=True, null=True)
    chk_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'linux_io_stat'


class LinuxIoStatHis(models.Model):
    tags = models.CharField(max_length=255)
    host = models.CharField(max_length=255)
    disk = models.CharField(max_length=255)
    rd_s = models.FloatField(blank=True, null=True)
    rd_avgkb = models.FloatField(blank=True, null=True)
    rd_m_s = models.FloatField(blank=True, null=True)
    rd_mrg_s = models.FloatField(blank=True, null=True)
    rd_cnc = models.FloatField(blank=True, null=True)
    rd_rt = models.FloatField(blank=True, null=True)
    wr_s = models.FloatField(blank=True, null=True)
    wr_avgkb = models.FloatField(blank=True, null=True)
    wr_m_s = models.FloatField(blank=True, null=True)
    wr_mrg_s = models.FloatField(blank=True, null=True)
    wr_cnc = models.FloatField(blank=True, null=True)
    wr_rt = models.FloatField(blank=True, null=True)
    busy = models.FloatField(blank=True, null=True)
    in_prg = models.FloatField(blank=True, null=True)
    io_s = models.FloatField(blank=True, null=True)
    qtime = models.FloatField(blank=True, null=True)
    stime = models.FloatField(blank=True, null=True)
    chk_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'linux_io_stat_his'