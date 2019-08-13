#! /usr/bin/python
# encoding:utf-8

import cx_Oracle
import MySQLdb
import time
import os
import paramiko
import re
# os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'

# 获取dbinfo,name,database_role,open_mode
def get_dbname_info(conn):
    cur = conn.cursor()
    dbname_sql = '''select name,db_unique_name,database_role,open_mode,log_mode,dbid,flashback_on from v$database'''
    cur.execute(dbname_sql)
    return cur.fetchall()

# 获取实例信息
def get_instance_info(conn):
    cur = conn.cursor()
    inst_sql = '''select instance_number,instance_name,host_name,startup_time,version from v$instance'''
    cur.execute(inst_sql)
    return cur.fetchall()

# 获取密码过期信息
def get_pwd_info(conn):
    cur = conn.cursor()
    pwd_sql = ''' select username, trunc(expiry_date - sysdate) result_number
  from dba_users
 where expiry_date is not null
   and account_status = 'OPEN'
   and expiry_date - sysdate <  7
   and username not in ('SYS')
 '''
    cur.execute(pwd_sql)
    return cur.fetchall()

# 获取归档使用情况
def get_archived(conn):
    cur = conn.cursor()
    archived_sql = ''' select percent_space_used from v$flash_recovery_area_usage a where a.file_type='ARCHIVED LOG' '''
    cur.execute(archived_sql)
    return cur.fetchall()

# 获取等待事件信息
def get_event_info(conn):
    cur = conn.cursor()
    event_sql = '''select event#, event, count(*) from v$session group by event#, event order by 3'''
    cur.execute(event_sql)
    return cur.fetchall()

# 获取无效索引
def get_invalid_index(conn):
    cur = conn.cursor()
    event_sql = '''select owner, index_name, '' partition_name, status
  from dba_indexes
 where status not in ('VALID', 'N/A')
union all
select i.owner, i.index_name, p.partition_name, p.status
  from dba_ind_partitions p, dba_indexes i
 where p.index_name = i.index_name
   and p.index_owner = i.owner
   and p.status != 'USABLE'
union all
select i.owner, i.index_name, s.subpartition_name, s.status
  from dba_ind_subpartitions s, dba_indexes i
 where s.index_name = i.index_name
   and s.index_name = i.index_name
   and s.status != 'USABLE' '''
    cur.execute(event_sql)
    return cur.fetchall()


# 获取锁等待信息
def get_lock_info(conn):
    cur = conn.cursor()
    lock_sql = '''SELECT DECODE(request, 0, 'Holder: ', 'Waiter: ') || SID sess,
       decode(lmode,
              0,
              'none',
              1,
              'null',
              2,
              'row share',
              3,
              'row exclusive',
              4,
              'share',
              5,
              'share row exclusive',
              6,
              'exclusive') lmode,
       ctime,
       inst_id,
       id1,
       id2,
       lmode,
       request,
       TYPE,
       sid session_id
  FROM gV$LOCK
 WHERE (id1, id2, TYPE) IN
       (SELECT id1, id2, TYPE FROM gV$LOCK WHERE request > 0)
 ORDER BY id1, request'''
    cur.execute(lock_sql)
    return cur.fetchall()

# 获取连接数信息
def check_process(conn):
    cur = conn.cursor()
    process_sql = '''select resource_name,current_utilization,limit_value,trunc(current_utilization * 100 / limit_value) Result_Number
  from v$resource_limit
 where resource_name in ('processes')'''
    cur.execute(process_sql)
    return cur.fetchall()

# 获取PGA使用率
def check_pga(conn):
    cur = conn.cursor()
    pga_sql = '''select round(b.value / 1024 / 1024, 1) pga_target,
       round(a.pga_used_mb, 1),
       round(a.pga_used_mb / (b.value / 1024 / 1024), 1) * 100  pga_used_pct
  from (select sum(PGA_ALLOC_MEM) / 1024 / 1024 pga_used_mb from v$process) a,
       v$parameter b
 where b.name = 'pga_aggregate_target' '''
    cur.execute(pga_sql)
    return cur.fetchall()

# 获取asm存储信息
def check_asm(conn):
    cur = conn.cursor()
    asm_sql = '''select name,state,total_mb,free_mb,usable_file_mb from v$asm_diskgroup'''
    cur.execute(asm_sql)
    return cur.fetchall()

# 获取adg传输延迟
def check_adg_trs(conn):
    cur = conn.cursor()
    adg_trs_sql = "select value,substr(value,2,2)*24*3600+substr(value,5,2)*3600+substr(value,8,2)*60+substr(value,11,2) from v$dataguard_stats where name='transport lag'"
    cur.execute(adg_trs_sql)
    return cur.fetchall()


# 获取adg应用延迟
def check_adg_apl(conn):
    cur = conn.cursor()
    adg_apl_sql = "select value,substr(value,2,2)*24*3600+substr(value,5,2)*3600+substr(value,8,2)*60+substr(value,11,2) from v$dataguard_stats where name='apply lag'"
    cur.execute(adg_apl_sql)
    return cur.fetchall()

# 获取表空间使用率
def check_tbs(conn):
    cur = conn.cursor()
    tbs_sql = '''SELECT DF.TABLESPACE_NAME,
       COUNT(*) DATAFILE_COUNT,
       ROUND(SUM(DF.BYTES) / 1048576 / 1024, 2) SIZE_GB,
       ROUND(SUM(FREE.BYTES) / 1048576 / 1024, 2) FREE_GB,
       ROUND(SUM(DF.BYTES) / 1048576 / 1024 -
             SUM(FREE.BYTES) / 1048576 / 1024,
             2) USED_GB,
       ROUND(MAX(FREE.MAXBYTES) / 1048576 / 1024, 2) MAXFREE,
       100 - ROUND(100.0 * SUM(FREE.BYTES) / SUM(DF.BYTES), 2) PCT_USED,
       ROUND(100.0 * SUM(FREE.BYTES) / SUM(DF.BYTES), 2) PCT_FREE
  FROM DBA_DATA_FILES DF,
       (SELECT TABLESPACE_NAME,
               FILE_ID,
               SUM(BYTES) BYTES,
               MAX(BYTES) MAXBYTES
          FROM DBA_FREE_SPACE
         WHERE BYTES > 1024 * 1024
         GROUP BY TABLESPACE_NAME, FILE_ID) FREE
 WHERE DF.TABLESPACE_NAME = FREE.TABLESPACE_NAME(+) AND DF.TABLESPACE_NAME NOT LIKE 'UNDO%'
   AND DF.FILE_ID = FREE.FILE_ID(+)
 GROUP BY DF.TABLESPACE_NAME
 ORDER BY 8'''
    cur.execute(tbs_sql)
    return cur.fetchall()

# 获取临时表空间使用率
def check_tmp_tbs(conn):
    cur = conn.cursor()
    tmp_tbs_sql = '''SELECT A.tablespace_name tablespace,
       D.mb_total,
       SUM(A.used_blocks * D.block_size) / 1024 / 1024 mb_used,
       trunc(100*SUM(A.used_blocks * D.block_size) / 1024 / 1024/D.mb_total) used_PCT
  FROM v$sort_segment A,
       (SELECT B.name, C.block_size, SUM(C.bytes) / 1024 / 1024 mb_total
          FROM v$tablespace B, v$tempfile C
         WHERE B.ts# = C.ts#
         GROUP BY B.name, C.block_size) D
 WHERE A.tablespace_name = D.name
 GROUP by A.tablespace_name, D.mb_total'''
    cur.execute(tmp_tbs_sql)
    return cur.fetchall()

# 获取undo表空间使用率
def check_undo_tbs(conn):
    cur = conn.cursor()
    undo_tbs_sql = '''select  b.tablespace_name,
       nvl(used_undo, 0) "USED_UNDO(M)",
       total_undo "Total_undo(M)",
       trunc(nvl(used_undo, 0) / total_undo * 100, 2) used_PCT
  from (select nvl(sum(bytes / 1024 / 1024), 0) used_undo, tablespace_name
          from dba_undo_extents
         where status in ('ACTIVE', 'UNEXPIRED')
           and tablespace_name in
               (select value from v$parameter where name = 'undo_tablespace')
         group by tablespace_name) a,
       (select tablespace_name, sum(bytes / 1024 / 1024) total_undo
          from dba_data_files
         where tablespace_name in
               (select upper(value) from v$parameter where name = 'undo_tablespace')
         group by tablespace_name) b
 where a.tablespace_name(+) = b.tablespace_name'''
    cur.execute(undo_tbs_sql)
    return cur.fetchall()

def get_para(conn,para):
    cur = conn.cursor()
    sql = "select a.VALUE from v$parameter a where a.name='%s' " %para
    cur.execute(sql)
    return cur.fetchall()

# 获取后台日志异常信息
def check_err(conn,host,user,password,ssh_port):
    cur = conn.cursor()
    diag_trace_sql = "select value from v$diag_info where name = 'Diag Trace'"
    cur.execute(diag_trace_sql)
    diag_trace = cur.fetchall()
    diag_trace_dir =  diag_trace[0][0]
    logfile = '%s/alert_*.log' %diag_trace_dir

    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(host, ssh_port, user, password)
    cmd = 'tail -300 %s |grep -A 3 ORA-' %logfile
    std_in, std_out, std_err = ssh_client.exec_command(cmd)
    stdout = std_out.read().decode('gbk')
    stderr = std_err.read().decode()
    return str(stdout)

# 获取Oracle状态数据， QPS、TPS等
def oracle_stat(conn):
    ora_stats = (
        "bytes received via SQL*Net from client",
        "bytes sent via SQL*Net to client",
        "consistent gets",
        "enqueue waits",
        "execute count",
        "leaf node splits",
        "logons cumulative",
        "parse count (total)",
        "parse count (hard)",
        "physical reads",
        "physical writes",
        "redo size",
        "sorts (memory)",
        "sorts (disk)",
        "table scans (long tables)",
        "table scans (short tables)",
        "transaction rollbacks",
        "user commits",
        "redo synch time",
        "redo synch writes",
        "user calls",
        "SQL*Net roundtrips to/from client",
        "gc cr blocks served",
        "gc cr blocks received",
        "gc cr block receive time",
        "gc cr block send time",
        "gc current blocks served",
        "gc current blocks received",
        "gc current block receive time",
        "gc current block send time",
        "gcs messages sent",
        "ges messages sent",
        "db block changes",
        "redo writes"
    )
    sql = """
            select name, value
            from v$sysstat
            where name in (%s)
            """
    stat_names = ",".join(("'" + s + "'" for s in ora_stats))
    sql_real = sql % (stat_names)
    cur = conn.cursor()
    cur.execute(sql_real)
    return cur.fetchall()

def oracle_osstat(conn):
    sql = """select stat_name, value from v$osstat
            where stat_name in ('PHYSICAL_MEMORY_BYTES', 'NUM_CPUS', 'IDLE_TIME', 'BUSY_TIME'
            )
        """
    cur = conn.cursor()
    cur.execute(sql)
    return cur.fetchall()


def oracle_time(conn):
    time_model = (
        'DB time',
        'DB CPU',
        'background cpu time'
    )
    stats = ",".join("'" + s + "'" for s in time_model)
    sql = """
            select stat_name, value
            from v$sys_time_model
            where stat_name in (%s)
        """ % stats
    cur = conn.cursor()
    cur.execute(sql)
    return cur.fetchall()





if __name__ == '__main__':
    user = 'dbmon'
    password = 'oracle'
    url = '192.168.48.10:1521/orcl'
    conn = cx_Oracle.connect(user, password, url)
    # 获取Oracle状态信息
    oracle_stat1 = {}
    res1 = oracle_stat(conn)
    for stat_name, stat_value in res1:
        oracle_stat1[stat_name] = stat_value
    oacle_osstat = {}
    rs = oracle_osstat(conn)
    for stat_name, value in rs:
        print stat_name, value

    print '等待1s获取Oracle实时状态'
    time.sleep(1)
    res2 = oracle_stat(conn)
    stat_delta = {}
    for stat_name, stat_value in res2:
        print stat_name, stat_value
        stat_delta[stat_name] = stat_value - oracle_stat1[stat_name]

