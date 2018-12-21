#! /usr/bin/python
# encoding:utf-8

import cx_Oracle
import paramiko
import math
import time
from datetime import datetime
from collections import defaultdict

def format_stat(label, stat_vals):
    ret = {}
    for i in range(len(label)):
        if ':' in label[i]:
            label_n, idx = label[i].split(':')
            idx = int(idx)
        else:
            label_n, idx = label[i], i

        ret[label_n] = round(stat_vals[i], 2)
    return ret

class Oraclestat(object):
    def __init__(self,conn):
        self.conn = conn
        self.proc_stat = {}
        self.last_time = time.time()
        self.loop_cnt = 0
        self.stat = {}
        self.old_stat = {}
        self.ora_stats = (
            "bytes received via SQL*Net from client",
            "bytes sent via SQL*Net to client",
            "session logical reads",
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
            "redo writes",
            "physical read total bytes",
            "physical write total bytes"
        )
        self.wait_events = (
            "db file sequential read",
            "db file scattered read",
            "log file parallel write",
            "log file sync",
            "log file parallel write",
            "enq: TX - row lock contention"
        )
        self.time_model = (
            'DB time',
            'DB CPU',
            'background cpu time'
        )

        self.os_stats = (
            'PHYSICAL_MEMORY_BYTES', 'NUM_CPUS', 'IDLE_TIME', 'BUSY_TIME'
        )



        self.old_stat = {}

        for stat in self.ora_stats:
            self.old_stat[stat] = 0

        for stat in self.wait_events:
            self.old_stat[stat] = 0
            self.old_stat[stat + '/time waited'] = 0

        for stat_name in self.time_model:
            self.old_stat[stat_name] = 0

        for stat_name in self.os_stats:
            self.old_stat[stat_name] = 0

    # def get_oracleinfo(self):


    def get_uptime(self):
        cur = self.conn.cursor()
        sql = "select startup_time, version, parallel from v$instance "
        cur.execute(sql)
        startup_time, version, parallel = cur.fetchone()
        uptime = datetime.now() - startup_time
        up_seconds = uptime.days * 86400 + uptime.seconds
        return up_seconds

    def get_oracle_pga(self):
        stat_name = 'sga size'
        cur = self.conn.cursor()
        sql = """select value from v$pgastat where name = 'total PGA allocated'
                    """
        cur.execute(sql)
        pga_size, =  cur.fetchone()
        return pga_size/1024/1024


    def get_oracle_sga(self):
        cur = self.conn.cursor()
        sql = """select sum(bytes) from v$sgainfo where name in (
                    'Fixed SGA Size',
                    'Redo Buffers',
                    'Buffer Cache Size',
                    'Shared Pool Size',
                    'Large Pool Size',
                    'Java Pool Size',
                    'Streams Pool Size',
                    'Shared IO Pool Size'
                )
            """
        cur.execute(sql)
        sga_size, = cur.fetchone()
        sql2 = "select bytes from  v$sgainfo where name = 'Granule Size'"
        cur.execute(sql2)
        granu_size, = cur.fetchone()
        return int(sga_size+granu_size-1)/granu_size*granu_size/1024/1024

    def get_oracle_mem(self):
        sga = self.get_oracle_sga()
        pga = self.get_oracle_pga()
        mem_phy = self.old_stat['PHYSICAL_MEMORY_BYTES']/1024/1024
        mem_pct = round(100*(pga+sga)/mem_phy,2)

        return {
            'sga size': sga,
            'pga size': pga,
            'mem pct':mem_pct
        }

    def get_oracle_stat(self):
        if self.loop_cnt == 0:
            elapsed = self.get_uptime()
        else:
            elapsed = time.time() - self.last_time

        self.last_time = time.time()
        self.loop_cnt += 1
        self.oracle_osstat()
        orastat = {}
        orastat['stat'] = self.get_ora_stat(elapsed)
        orastat['wait'] = self.get_wait_events(elapsed)
        orastat['sess'] = self.get_oracle_session_count()
        orastat['time'] = self.get_oracle_time(elapsed)
        orastat['mem'] = self.get_oracle_mem()
        return orastat

    # 获取Oracle状态数据， QPS、TPS等
    def get_ora_stat(self,elapsed):
        sql = """
                select name, value
                from v$sysstat
                where name in (%s)
                """
        stat_names = ",".join(("'" + s + "'" for s in self.ora_stats))
        sql_real = sql % (stat_names)
        cur = self.conn.cursor()
        cur.execute(sql_real)
        rs = cur.fetchall()
        stat_delta = {}
        for stat_name, stat_val in rs:
            stat_delta[stat_name] = math.ceil((stat_val - self.old_stat[stat_name]) * 1.0 / elapsed)
            self.old_stat[stat_name] = stat_val

        return {
            'qps': stat_delta['execute count'],
            'tps': stat_delta['user commits'] + stat_delta['transaction rollbacks'],
            'gets': stat_delta['consistent gets'],
            'logr': stat_delta['session logical reads'],
            'phyr': stat_delta['physical reads'],
            'phyw': stat_delta['physical writes'],
            'blockchange': stat_delta['db block changes'],
            'redo': math.ceil(stat_delta['redo size'] / 1024),
            'parse': stat_delta['parse count (total)'],
            'hardparse': stat_delta['parse count (hard)'],
            'netin': math.ceil(stat_delta['bytes received via SQL*Net from client'] / 1024),
            'netout': math.ceil(stat_delta['bytes sent via SQL*Net to client'] / 1024),
            'execute count': stat_delta['execute count'],
            'user commits': stat_delta['user commits'],
            'redow': stat_delta['redo writes'],
            'io_throughput':round(stat_delta['physical read total bytes']/1024/1024 + stat_delta['physical write total bytes']/1024/1024,2)
        }

    def get_wait_events(self, elapsed):
        cur = self.conn.cursor()
        sql_wait = """
              select /* dbagent */event, total_waits, round(time_waited_micro/1000,2) as time_waited
              from v$system_event
              where event in (%s)
          """
        event_names = ",".join("'" + s + "'" for s in self.wait_events)

        sql_real = sql_wait % event_names

        rs = cur.execute(sql_real)

        stat_delta = defaultdict(int)
        for event, total_waits, time_waited in rs:
            waits = total_waits - self.old_stat[event]
            if waits == 0:
                stat_delta[event + "/avg waitim"] = 0
                stat_delta[event] = 0
            else:
                stat_delta[event + "/avg waitim"] = math.ceil(
                    (time_waited - self.old_stat[event + "/time waited"]) * 1.0 / waits)
                stat_delta[event] = math.ceil(
                    (total_waits - self.old_stat[event]))

            self.old_stat[event] = total_waits
            self.old_stat[event + "/time waited"] = time_waited

        return {
            'log_sync_wait': stat_delta['log file sync/avg waitim'],
            'log_sync_cnt': stat_delta['log file sync'],
            'log_para_wait': stat_delta['log file parallel write/avg waitim'],
            'scat_wait': stat_delta['db file scattered read/avg waitim'],
            'scat_read_cnt': stat_delta['db file scattered read'],
            'seq_wait': stat_delta['db file sequential read/avg waitim'],
            'seq_read_cnt': stat_delta['db file sequential read'],
            'row_lock_cnt': stat_delta['enq: TX - row lock contention']
        }

    def get_oracle_session_count(self):
        cur = self.conn.cursor()
        sql = """
            select count(*) as total_sess,
            sum(case when status='ACTIVE' and type = 'USER' then 1 else 0 end) as act_sess,
            sum(case when status='ACTIVE' and type = 'USER' and command in (2,6,7) then 1 else 0 end) as act_trans,
            sum(case when blocking_session is not null then 1 else 0 end) as blocked_sessions
        from v$session
        """
        #v$sqlcommand
        cur.execute(sql)
        total_sess, act_sess, act_trans,blocked_sess = cur.fetchone()
        return {
            'total': total_sess,
            'act': act_sess,
            'act_trans': act_trans,
            'blocked':blocked_sess
        }

    def oracle_osstat(self):
        sql = """select stat_name, value from v$osstat
                where stat_name in ('PHYSICAL_MEMORY_BYTES', 'NUM_CPUS', 'IDLE_TIME', 'BUSY_TIME'
                )
            """
        cur = self.conn.cursor()
        cur.execute(sql)
        rs  = cur.fetchall()
        cpu_idle = 0
        cpu_busy = 0

        for stat_name, value in rs:
            if stat_name == 'IDLE_TIME':
                cpu_idle = value - self.old_stat[stat_name]
            elif stat_name == 'BUSY_TIME':
                cpu_busy = value - self.old_stat[stat_name]
            self.old_stat[stat_name] = value

        if cpu_idle + cpu_busy == 0:
            self.stat['host_cpu'] = 0
        else:
            self.stat['host_cpu'] = max(round(100.0 * cpu_busy / (cpu_idle + cpu_busy), 2), 0)


    def get_oracle_time(self,elapsed):
        stats = ",".join("'" + s + "'" for s in self.time_model)
        sql = """
                select stat_name, value
                from v$sys_time_model
                where stat_name in (%s)
            """ % stats
        cur = self.conn.cursor()
        cur.execute(sql)
        rs = cur.fetchall()
        stat_delta = {}
        num_cpu = self.old_stat.get('NUM_CPUS', 1)
        for stat_name, value in rs:
            diff_val = max((value - self.old_stat[stat_name]) * 1.0 / elapsed, 0)
            if stat_name in ('DB time', 'DB CPU', 'background cpu time'):
                diff_val /= 10000.0 * num_cpu
            stat_delta[stat_name] = round(diff_val, 2)
            self.old_stat[stat_name] = value

        return {
            'dbtime': stat_delta['DB time'],
            'dbcpu': stat_delta['DB CPU'],
            'bgcpu': stat_delta['background cpu time']
        }


if __name__ == '__main__':
    user = 'dbmon'
    password = 'oracle'
    url = '192.168.48.10:1521/orcl'
    conn = cx_Oracle.connect(user, password, url)
    oraclestat = Oraclestat(conn)
    while True:
        print oraclestat.get_oracle_stat()
        time.sleep(1)


