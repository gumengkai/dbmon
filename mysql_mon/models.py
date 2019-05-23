from django.db import models

# Create your models here.

class MysqlDb(models.Model):
    host = models.CharField(max_length=255)
    port = models.CharField(max_length=255)
    tags = models.CharField(max_length=255)
    version = models.CharField(max_length=255, blank=True, null=True)
    uptime = models.IntegerField(blank=True, null=True)
    mysql_datadir = models.CharField(max_length=255)
    mysql_slow_query = models.CharField(max_length=255)
    mysql_binlog = models.CharField(max_length=255)
    max_connections = models.CharField(max_length=255, blank=True, null=True)
    max_connect_errors = models.IntegerField(blank=True, null=True)
    threads_connected = models.IntegerField(blank=True, null=True)
    threads_running = models.IntegerField(blank=True, null=True)
    threads_created = models.IntegerField(blank=True, null=True)
    threads_cached = models.IntegerField(blank=True, null=True)
    threads_waited = models.IntegerField(blank=True, null=True)
    conn_rate = models.CharField(max_length=255, blank=True, null=True)
    conn_rate_level = models.CharField(max_length=255, blank=True, null=True)
    qps = models.IntegerField(db_column='QPS', blank=True, null=True)  # Field name made lowercase.
    tps = models.IntegerField(db_column='TPS', blank=True, null=True)  # Field name made lowercase.
    bytes_received = models.IntegerField(blank=True, null=True)
    bytes_send = models.IntegerField(blank=True, null=True)
    open_files_limit = models.IntegerField(blank=True, null=True)
    open_files = models.IntegerField(blank=True, null=True)
    table_open_cache = models.IntegerField(blank=True, null=True)
    open_tables = models.IntegerField(blank=True, null=True)
    key_buffer_size = models.FloatField()
    sort_buffer_size = models.FloatField()
    join_buffer_size = models.FloatField()
    key_blocks_unused = models.IntegerField(blank=True, null=True)
    key_blocks_used = models.IntegerField(blank=True, null=True)
    key_blocks_not_flushed = models.IntegerField(blank=True, null=True)
    key_blocks_used_rate = models.FloatField()
    key_buffer_read_rate = models.FloatField()
    key_buffer_write_rate = models.FloatField()
    mysql_sel = models.IntegerField()
    mysql_ins = models.IntegerField()
    mysql_upd = models.IntegerField()
    mysql_del = models.IntegerField()
    select_scan = models.IntegerField()
    slow_queries = models.IntegerField()
    key_read_requests = models.IntegerField()
    key_reads = models.IntegerField()
    key_write_requests = models.IntegerField()
    Key_writes = models.IntegerField()
    innodb_buffer_pool_size = models.FloatField()
    innodb_buffer_pool_pages_total = models.IntegerField()
    innodb_buffer_pool_pages_data = models.IntegerField()
    innodb_buffer_pool_pages_dirty = models.IntegerField()
    innodb_buffer_pool_pages_flushed = models.IntegerField()
    innodb_buffer_pool_pages_free = models.IntegerField()
    innodb_buffer_pool_hit = models.FloatField()
    innodb_buffer_usage = models.FloatField()
    innodb_buffer_dirty_rate = models.FloatField()
    innodb_io_capacity = models.IntegerField()
    innodb_read_io_threads = models.IntegerField()
    innodb_write_io_threads = models.IntegerField()
    innodb_rows_deleted_persecond = models.IntegerField()
    innodb_rows_inserted_persecond = models.IntegerField()
    innodb_rows_read_persecond = models.IntegerField()
    innodb_rows_updated_persecond = models.IntegerField()
    innodb_row_lock_waits = models.IntegerField()
    innodb_row_lock_time_avg = models.FloatField()
    innodb_buffer_pool_pages_flushed_delta = models.IntegerField()
    innodb_data_read = models.FloatField()
    innodb_data_written = models.FloatField()
    innodb_data_reads = models.IntegerField()
    innodb_data_writes = models.IntegerField()
    innodb_log_writes = models.IntegerField()
    innodb_os_log_written = models.FloatField()
    mon_status = models.CharField(max_length=255)
    rate_level = models.CharField(max_length=255)
    chk_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mysql_db'


class MysqlDbHis(models.Model):
    host = models.CharField(max_length=255)
    port = models.CharField(max_length=255)
    tags = models.CharField(max_length=255)
    version = models.CharField(max_length=255, blank=True, null=True)
    uptime = models.IntegerField(blank=True, null=True)
    mysql_datadir = models.CharField(max_length=255)
    mysql_slow_query = models.CharField(max_length=255)
    mysql_binlog = models.CharField(max_length=255)
    max_connections = models.CharField(max_length=255, blank=True, null=True)
    max_connect_errors = models.IntegerField(blank=True, null=True)
    threads_connected = models.IntegerField(blank=True, null=True)
    threads_running = models.IntegerField(blank=True, null=True)
    threads_created = models.IntegerField(blank=True, null=True)
    threads_cached = models.IntegerField(blank=True, null=True)
    threads_waited = models.IntegerField(blank=True, null=True)
    conn_rate = models.CharField(max_length=255, blank=True, null=True)
    conn_rate_level = models.CharField(max_length=255, blank=True, null=True)
    qps = models.IntegerField(db_column='QPS', blank=True, null=True)  # Field name made lowercase.
    tps = models.IntegerField(db_column='TPS', blank=True, null=True)  # Field name made lowercase.
    bytes_received = models.IntegerField(blank=True, null=True)
    bytes_send = models.IntegerField(blank=True, null=True)
    open_files_limit = models.IntegerField(blank=True, null=True)
    open_files = models.IntegerField(blank=True, null=True)
    table_open_cache = models.IntegerField(blank=True, null=True)
    open_tables = models.IntegerField(blank=True, null=True)
    key_buffer_size = models.FloatField()
    sort_buffer_size = models.FloatField()
    join_buffer_size = models.FloatField()
    key_blocks_unused = models.IntegerField(blank=True, null=True)
    key_blocks_used = models.IntegerField(blank=True, null=True)
    key_blocks_not_flushed = models.IntegerField(blank=True, null=True)
    key_blocks_used_rate = models.FloatField()
    key_buffer_read_rate = models.FloatField()
    key_buffer_write_rate = models.FloatField()
    mysql_sel = models.IntegerField()
    mysql_ins = models.IntegerField()
    mysql_upd = models.IntegerField()
    mysql_del = models.IntegerField()
    select_scan = models.IntegerField()
    slow_queries = models.IntegerField()
    key_read_requests = models.IntegerField()
    key_reads = models.IntegerField()
    key_write_requests = models.IntegerField()
    Key_writes = models.IntegerField()
    innodb_buffer_pool_size = models.FloatField()
    innodb_buffer_pool_pages_total = models.IntegerField()
    innodb_buffer_pool_pages_data = models.IntegerField()
    innodb_buffer_pool_pages_dirty = models.IntegerField()
    innodb_buffer_pool_pages_flushed = models.IntegerField()
    innodb_buffer_pool_pages_free = models.IntegerField()
    innodb_buffer_pool_hit = models.FloatField()
    innodb_buffer_usage = models.FloatField()
    innodb_buffer_dirty_rate = models.FloatField()
    innodb_io_capacity = models.IntegerField()
    innodb_read_io_threads = models.IntegerField()
    innodb_write_io_threads = models.IntegerField()
    innodb_rows_deleted_persecond = models.IntegerField()
    innodb_rows_inserted_persecond = models.IntegerField()
    innodb_rows_read_persecond = models.IntegerField()
    innodb_rows_updated_persecond = models.IntegerField()
    innodb_row_lock_waits = models.IntegerField()
    innodb_row_lock_time_avg = models.FloatField()
    innodb_buffer_pool_pages_flushed_delta = models.IntegerField()
    innodb_data_read = models.FloatField()
    innodb_data_written = models.FloatField()
    innodb_data_reads = models.IntegerField()
    innodb_data_writes = models.IntegerField()
    innodb_log_writes = models.IntegerField()
    innodb_os_log_written = models.FloatField()
    mon_status = models.CharField(max_length=255)
    rate_level = models.CharField(max_length=255)
    chk_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'mysql_db_his'


class MysqlDbRate(models.Model):
    host = models.CharField(max_length=255)
    port = models.CharField(max_length=255)
    tags = models.CharField(max_length=255)
    conn_decute = models.IntegerField()
    cpu_decute = models.IntegerField()
    mem_decute = models.IntegerField()
    disk_decute = models.IntegerField()
    db_rate = models.IntegerField()
    db_rate_level = models.CharField(max_length=255)
    db_rate_color = models.CharField(max_length=255)
    db_rate_reason = models.CharField(max_length=255)
    rate_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'mysql_db_rate'


class MysqlDbRateHis(models.Model):
    host = models.CharField(max_length=255)
    port = models.CharField(max_length=255)
    tags = models.CharField(max_length=255)
    conn_decute = models.IntegerField()
    cpu_decute = models.IntegerField()
    mem_decute = models.IntegerField()
    disk_decute = models.IntegerField()
    db_rate = models.IntegerField()
    db_rate_level = models.CharField(max_length=255)
    db_rate_color = models.CharField(max_length=255)
    db_rate_reason = models.CharField(max_length=255)
    rate_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'mysql_db_rate_his'


class MysqlRepl(models.Model):
    tags = models.CharField(max_length=255)
    server_id = models.CharField(max_length=255)
    host = models.CharField(max_length=255)
    port = models.CharField(max_length=255)
    is_master = models.CharField(max_length=255, blank=True, null=True)
    is_slave = models.CharField(max_length=255, blank=True, null=True)
    mysql_role = models.CharField(max_length=255, blank=True, null=True)
    read_only = models.CharField(max_length=255, blank=True, null=True)
    master_server = models.CharField(max_length=255, blank=True, null=True)
    master_port = models.CharField(max_length=255, blank=True, null=True)
    slave_io_run = models.CharField(max_length=255, blank=True, null=True)
    slave_io_rate = models.CharField(max_length=255, blank=True, null=True)
    slave_sql_run = models.CharField(max_length=255, blank=True, null=True)
    slave_sql_rate = models.CharField(max_length=255, blank=True, null=True)
    delay = models.CharField(max_length=255, blank=True, null=True)
    delay_rate = models.CharField(max_length=255, blank=True, null=True)
    current_binlog_file = models.CharField(max_length=255, blank=True, null=True)
    current_binlog_pos = models.CharField(max_length=255, blank=True, null=True)
    master_binlog_file = models.CharField(max_length=255, blank=True, null=True)
    master_binlog_pos = models.CharField(max_length=255, blank=True, null=True)
    master_binlog_space = models.CharField(max_length=255, blank=True, null=True)
    chk_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mysql_repl'


class MysqlReplHis(models.Model):
    tags = models.CharField(max_length=255)
    server_id = models.CharField(max_length=255)
    host = models.CharField(max_length=255)
    port = models.CharField(max_length=255)
    is_master = models.CharField(max_length=255, blank=True, null=True)
    is_slave = models.CharField(max_length=255, blank=True, null=True)
    mysql_role = models.CharField(max_length=255, blank=True, null=True)
    read_only = models.CharField(max_length=255, blank=True, null=True)
    master_server = models.CharField(max_length=255, blank=True, null=True)
    master_port = models.CharField(max_length=255, blank=True, null=True)
    slave_io_run = models.CharField(max_length=255, blank=True, null=True)
    slave_io_rate = models.CharField(max_length=255, blank=True, null=True)
    slave_sql_run = models.CharField(max_length=255, blank=True, null=True)
    slave_sql_rate = models.CharField(max_length=255, blank=True, null=True)
    delay = models.CharField(max_length=255, blank=True, null=True)
    delay_rate = models.CharField(max_length=255, blank=True, null=True)
    current_binlog_file = models.CharField(max_length=255, blank=True, null=True)
    current_binlog_pos = models.CharField(max_length=255, blank=True, null=True)
    master_binlog_file = models.CharField(max_length=255, blank=True, null=True)
    master_binlog_pos = models.CharField(max_length=255, blank=True, null=True)
    master_binlog_space = models.CharField(max_length=255, blank=True, null=True)
    chk_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mysql_repl_his'

class TabMysqlServers(models.Model):
    tags = models.CharField(max_length=255)
    host = models.CharField(max_length=255)
    port = models.CharField(max_length=255)
    user = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    user_os = models.CharField(max_length=255)
    password_os = models.CharField(max_length=255)
    ssh_port_os = models.IntegerField()
    connect = models.CharField(max_length=255, blank=True, null=True)
    repl = models.CharField(max_length=255, blank=True, null=True)
    conn = models.CharField(max_length=255, blank=True, null=True)
    err_info = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tab_mysql_servers'


class MysqlBigTable(models.Model):
    host = models.CharField(max_length=255)
    tags = models.CharField(max_length=255)
    db = models.CharField(max_length=255)
    table_name = models.CharField(max_length=255)
    total = models.FloatField()
    chk_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mysql_big_table'

class MysqlBigTableHis(models.Model):
    host = models.CharField(max_length=255)
    tags = models.CharField(max_length=255)
    db = models.CharField(max_length=255)
    table_name = models.CharField(max_length=255)
    total = models.FloatField()
    chk_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mysql_big_table_his'

class MysqlSlowquery(models.Model):
    host = models.CharField(max_length=255)
    port = models.CharField(max_length=255)
    tags = models.CharField(max_length=255)
    slow_log_file = models.CharField(max_length=255)
    start_time  = models.CharField(max_length=255)
    client_host = models.CharField(max_length=255)
    db_name = models.CharField(max_length=255)
    sql_text = models.TextField()
    slow_log_file = models.CharField(max_length=255)
    query_time = models.FloatField()
    lock_time = models.FloatField()
    rows_examined = models.IntegerField(blank=True, null=True)
    rows_sent = models.IntegerField(blank=True, null=True)
    thread_id = models.CharField(max_length=255)
    chk_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mysql_slowquery'