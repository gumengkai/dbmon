#! /usr/bin/python
# encoding:utf-8

import base64
import sys
import time
from datetime import  datetime
from multiprocessing import Process;

import MySQLdb
import cx_Oracle
import paramiko

import check_mysql as check_msql
import check_oracle as check_ora
import check_os as check_os
from check_linux import LinuxStat
import log_parser
import tools as tools
import alarm as alarm
import my_log as my_log
from oracle_stat import  Oraclestat
from redis_stat import Redisstat
import web_check
reload(sys)
sys.setdefaultencoding('utf-8')
# 配置文件
import ConfigParser
import os
import redis as Rds


def check_linux(tags,host,host_name,user,password,ssh_port):
    # 密钥解密
    password = base64.decodestring(password)
    my_log.logger.info('%s：开始获取系统监控信息' % tags)
    # 连通性检查
    conn = False
    try:
        # 初始化ssh连接
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(host, ssh_port, user, password)
        conn = True
    except Exception, e:
        error_msg = "%s 目标主机连接失败：%s" % (tags, str(e))
        os_rate_level = 'red'
        my_log.logger.error(error_msg)
        insert_sql = "insert into os_info_his select * from os_info where tags = '%s'" % tags
        tools.mysql_exec(insert_sql, '')
        delete_sql = "delete from os_info where tags='%s'" % tags
        tools.mysql_exec(delete_sql, '')
        error_sql = "insert into os_info(tags,host,host_name,mon_status,rate_level) values(%s,%s,%s,%s,%s)"
        value = (tags,host, host_name, 'connected error',os_rate_level)
        tools.mysql_exec(error_sql, value)
        # 更新linux主机打分信息
        my_log.logger.info('%s :开始更新linux主机评分信息' %tags)
        delete_sql = "delete from linux_rate where tags= '%s'" % tags
        tools.mysql_exec(delete_sql, '')
        insert_sql = "insert into linux_rate(host,tags,linux_rate,linux_rate_level,linux_rate_color,linux_rate_reason) select host,tags,'0','danger','red','connected error' from tab_linux_servers where tags ='%s'" % tags
        tools.mysql_exec(insert_sql, '')
        my_log.logger.info('%s扣分明细，总评分:%s,扣分原因:%s' % (tags,'0', 'connected error'))

    if conn:
        # linux数据采集
        linuxstat = LinuxStat(host, user, password, ssh_client)

        uptime = linuxstat.get_uptime()
        up_days = round(float(uptime) / 60 / 60 / 24, 2)
        stat = linuxstat.get_linux()

        # 主机信息
        hostinfo = stat['hostinfo']
        hostname = hostinfo['hostname']
        ostype = hostinfo['ostype']
        kernel = hostinfo['kernel']
        frame = hostinfo['frame']
        linux_version = hostinfo['linux_version']

        # cpu信息
        cpuinfo = stat['cpuinfo']
        cpu_mode = cpuinfo['cpu_mode']
        cpu_cache = cpuinfo['cpu_cache']
        processor = cpuinfo['processor']
        virtual = cpuinfo['virtual']
        cpu_speed = cpuinfo['cpu_speed']

        # 内存信息
        Memtotal = stat['Memtotal']
        memtotal = float(Memtotal['Memtotal']) / 1024 / 1024

        memstat = stat['mem']
        mem_cache = memstat['cache']
        mem_buffer = memstat['buffer']
        mem_free = memstat['free']
        mem_used_mb = memstat['used']
        swap_used = memstat['swap_used']
        swap_free = memstat['swap_free']

        # ip地址
        ipinfo = stat['ipinfo']
        ip = ipinfo['ipinfo']

        # 网卡流量
        net_stat = stat['net']
        recv_kbps = 0
        send_kbps = 0
        my_log.logger.info('%s：初始化linux_net表' % tags)
        insert_sql = "insert into linux_net_his select * from linux_net where tags = '%s'" % tags
        tools.mysql_exec(insert_sql, '')
        delete_sql = "delete from linux_net where tags = '%s'" % tags
        tools.mysql_exec(delete_sql, '')
        for nic in net_stat:
            nic_name = nic['nic']
            nic_recv = nic['recv']
            nic_send = nic['send']
            insert_net_sql = 'insert into linux_net(tags,nic,recv,send) values(%s,%s,%s,%s)'
            value = (tags, nic_name, nic_recv, nic_send)
            my_log.logger.info('%s：获取网卡流量(网卡：%s 接收：%s 发送：%s)' % (tags, nic_name, nic_recv, nic_send))
            tools.mysql_exec(insert_net_sql, value)
            recv_kbps = recv_kbps + nic_recv
            send_kbps = send_kbps + nic_send

        # 磁盘IO
        all_iops = 0
        all_read_mb = 0
        all_write_mb = 0
        io_stat = stat['iostat']
        my_log.logger.info('%s：初始化linux_io_stat表' % tags)
        insert_sql = "insert into linux_io_stat_his select * from linux_io_stat where tags = '%s'" % tags
        tools.mysql_exec(insert_sql, '')
        delete_sql = "delete from linux_io_stat where tags = '%s'" % tags
        tools.mysql_exec(delete_sql, '')
        for each in io_stat:
            disk = each['disk']
            rd_s = each['rd_s']
            rd_avgkb = each['rd_avgkb']
            rd_m_s = each['rd_m_s']
            rd_mrg_s = each['rd_mrg_s']
            rd_cnc = each['rd_cnc']
            rd_rt = each['rd_rt']
            wr_s = each['wr_s']
            wr_avgkb = each['wr_avgkb']
            wr_m_s = each['wr_m_s']
            wr_mrg_s = each['wr_mrg_s']
            wr_cnc = each['wr_cnc']
            wr_rt = each['wr_rt']
            busy = each['busy']
            in_prg = each['in_prg']
            io_s = each['io_s']
            qtime = each['qtime']
            stime = each['stime']

            insert_io_sql = 'insert into linux_io_stat(tags,host,disk,rd_s,rd_avgkb,rd_m_s,rd_mrg_s,rd_cnc,rd_rt,wr_s,wr_avgkb,wr_m_s,wr_mrg_s,' \
                            'wr_cnc,wr_rt,busy,in_prg,io_s,qtime,stime) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
            value = (
                tags, host, disk, rd_s, rd_avgkb, rd_m_s, rd_mrg_s, rd_cnc, rd_rt, wr_s, wr_avgkb, wr_m_s, wr_mrg_s,
                wr_cnc,
                wr_rt, busy, in_prg, io_s, qtime, stime)
            my_log.logger.info('%s：获取磁盘IO(磁盘名：%s 读取量：%s 写入量：%s)' % (tags, disk, rd_m_s, wr_m_s))
            tools.mysql_exec(insert_io_sql, value)

            all_iops = all_iops + io_s
            all_read_mb = all_read_mb + rd_m_s
            all_write_mb = all_write_mb + wr_m_s

        # load
        load_stat = stat['load']
        load1 = load_stat['load1']
        load5 = load_stat['load5']
        load15 = load_stat['load15']

        # cpu使用率
        cpu_stat = stat['cpu']
        cpu_sys = cpu_stat['sys']
        cpu_iowait = cpu_stat['iowait']
        cpu_user = cpu_stat['user']
        cpu_used = 100 - float(cpu_stat['idle'])

        # 内存使用率
        mem_stat = stat['mem']
        mem_buffer = mem_stat['buffer']
        mem_cache = mem_stat['cache']
        mem_use = mem_stat['used']
        mem_free = mem_stat['free']

        # 虚拟内存
        vm_stat = stat['vmstat']
        pgin = vm_stat['pgin']
        pgout = vm_stat['pgout']
        swapin = vm_stat['swapin']
        swapout = vm_stat['swapout']
        pgfault = vm_stat['pgfault']
        pgmajfault = vm_stat['pgmajfault']

        # 进程信息
        proc_stat = stat['proc']
        proc_new = proc_stat['new']
        proc_runing = proc_stat['running']
        proc_block = proc_stat['block']
        intr = proc_stat['intr']
        ctx = proc_stat['ctx']
        softirq = proc_stat['softirq']

        # (老版本)发送网络流量，接收网络流量，cpu使用率
        # recv_kbps,send_kbps,cpu_used = check_os.os_get_info(host, user, password)
        # tcp连接数
        tcp_stat = stat['tcpstat']
        tcp_close = tcp_stat['close']
        tcp_timewait = tcp_stat['timewait']
        tcp_connected = tcp_stat['connected']
        tcp_syn = tcp_stat['syn']
        tcp_listen = tcp_stat['listen']
        # cpu使用率评级
        cpu_rate_level = tools.get_rate_level(float(cpu_used))
        mem_used = check_os.os_get_mem(host, ssh_port, user, password)
        # 内存使用率评级
        mem_rate_level = tools.get_rate_level(float(mem_used))
        # 主机状态评级
        os_rate_level = 'green'

        # 归档osinfo历史数据
        my_log.logger.info('%s：初始化os_info表' % tags)
        insert_sql = "insert into os_info_his select * from os_info where tags = '%s'" % tags
        tools.mysql_exec(insert_sql, '')
        delete_sql = "delete from os_info where tags = '%s'" % tags
        tools.mysql_exec(delete_sql, '')

        insert_os_info_sql = 'insert into os_info(tags,host,ssh_port,host_name,updays,recv_kbps,send_kbps,load1,load5,load15,cpu_sys,cpu_iowait,cpu_user,cpu_used,cpu_rate_level,' \
                             'mem_used,mem_cache,mem_buffer,mem_free,mem_used_mb,swap_used,swap_free,pgin,pgout,swapin,swapout,pgfault,pgmajfault,mem_rate_level,' \
                             'tcp_close,tcp_timewait,tcp_connected,tcp_syn,tcp_listen,' \
                             'iops,read_mb,write_mb,proc_new,proc_running,proc_block,intr,ctx,softirq,' \
                             'hostname,ostype,kernel,frame,linux_version,cpu_mode,cpu_cache,processor,virtual_cnt,cpu_speed,Memtotal,ipinfo,mon_status,rate_level) ' \
                             'value(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        value = (tags, host, ssh_port,host_name, up_days, recv_kbps, send_kbps, load1, load5, load15,
                 cpu_sys, cpu_iowait, cpu_user, cpu_used, cpu_rate_level,
                 mem_used, mem_cache, mem_buffer, mem_free, mem_used_mb, swap_used, swap_free, pgin, pgout, swapin,
                 swapout,
                 pgfault, pgmajfault, mem_rate_level,
                 tcp_close, tcp_timewait, tcp_connected, tcp_syn, tcp_listen,
                 all_iops, all_read_mb, all_write_mb,
                 proc_new, proc_runing, proc_block, intr, ctx, softirq,
                 hostname, ostype, kernel, frame, linux_version, cpu_mode, cpu_cache, processor, virtual, cpu_speed,
                 memtotal, ip,
                 'connected', os_rate_level)

        my_log.logger.info('%s：获取系统监控数据(CPU：%s MEM：%s)' % (tags, cpu_used, mem_used))
        # print insert_cpu_used_sql
        tools.mysql_exec(insert_os_info_sql, value)

        my_log.logger.info('%s：开始获取文件系统监控信息' % tags)

        file_sys = check_os.os_get_disk(host,ssh_port, user, password)

        # 归档os_filesystem_his历史数据
        my_log.logger.info('%s：初始化os_filesystem表' % tags)
        insert_sql = "insert into os_filesystem_his select * from os_filesystem where tags = '%s'" % tags
        tools.mysql_exec(insert_sql, '')
        delete_sql = "delete from os_filesystem where tags = '%s'" % tags
        tools.mysql_exec(delete_sql, '')

        for i in xrange(len(file_sys)):
            disk_rate = float(file_sys[i]['used'].replace('%', ''))
            disk_rate_level = tools.get_rate_level(float(file_sys[i]['used'].replace('%', '')))
            insert_file_sys_sql = "insert into os_filesystem(tags,host,host_name,name,size,avail,pct_used,filesystem,disk_rate_level) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            value = (
                tags, host, host_name, file_sys[i]['name'], file_sys[i]['size'], file_sys[i]['avail'],
                file_sys[i]['used'].replace('%', ''), file_sys[i]['filesystem'], disk_rate_level)
            my_log.logger.info('%s：获取文件系统使用率(路径名：%s 使用率：%s)' % (tags, file_sys[i]['name'], file_sys[i]['used']))
            tools.mysql_exec(insert_file_sys_sql, value)

        # 更新主机评分信息
        my_log.logger.info('%s :开始更新Linux主机评分信息' % tags)

        # 内存使用率扣分
        linux_mem_decute_reason = ''
        mem_stat = tools.mysql_query(
            "select host,host_name,mem_used from os_info where mem_used is not null and host = '%s'" % host)
        if mem_stat == 0:
            my_log.logger.warning('%s：内存使用率未采集到数据' % host)
            linux_mem_decute = 0
        else:
            linux_mem_used = float(mem_stat[0][2])
            linux_mem_decute = tools.get_decute(linux_mem_used)
            if linux_mem_decute <> 0:
                linux_mem_decute_reason = '内存使用率：%d%% \n' % linux_mem_used
            else:
                linux_mem_decute_reason = ''

        # cpu使用率扣分
        linux_cpu_decute_reason = ''
        cpu_stat = tools.mysql_query(
            "select host,host_name,cpu_used from os_info where cpu_used is not null and host = '%s'" % host)
        if cpu_stat == 0:
            my_log.logger.warning('%s：CPU使用率未采集到数据' % host)
            linux_cpu_decute = 0
        else:
            linux_cpu_used = float(cpu_stat[0][2])
            linux_cpu_decute = tools.get_decute(linux_cpu_used)
            if linux_cpu_decute <> 0:
                linux_cpu_decute_reason = 'CPU使用率：%d%% \n' % linux_cpu_used
            else:
                linux_cpu_decute_reason = ''

        linux_top_decute = max(linux_cpu_decute, linux_mem_decute)
        linux_all_rate = 100 - linux_top_decute
        if linux_all_rate >= 60:
            linux_rate_color = 'green'
            linux_rate_level = 'success'
        elif linux_all_rate >= 20 and linux_all_rate < 60:
            linux_rate_color = 'yellow'
            linux_rate_level = 'warning'
        else:
            linux_rate_color = 'red'
            linux_rate_level = 'danger'
        linux_all_decute_reason = linux_cpu_decute_reason + linux_mem_decute_reason

        # 删除历史数据
        delete_sql = "delete from linux_rate where tags= '%s'" % tags
        tools.mysql_exec(delete_sql, '')

        # 插入总评分及扣分明细
        insert_sql = "insert into linux_rate(host,tags,cpu_decute,mem_decute,linux_rate,linux_rate_level,linux_rate_color,linux_rate_reason) select host,tags,'%s','%s','%s','%s','%s','%s' from tab_linux_servers where tags ='%s'" % (
            linux_cpu_decute, linux_mem_decute, linux_all_rate, linux_rate_level, linux_rate_color,
            linux_all_decute_reason, tags)
        tools.mysql_exec(insert_sql, '')
        my_log.logger.info('%s扣分明细，cpu使用率扣分:%s，内存使用率扣分:%s，总评分:%s,扣分原因:%s' % (
            tags, linux_cpu_decute, linux_mem_decute, linux_all_rate, linux_all_decute_reason))


def check_oracle(tags,host,port,service_name,user,password,user_cdb,password_cdb,service_name_cdb,user_os,password_os,ssh_port_os,version):
    my_log.logger.info('%s等待2秒待linux主机信息采集完毕' %tags)
    time.sleep(2)
    password = base64.decodestring(password)
    password_os = base64.decodestring(password_os)
    password_cdb = base64.decodestring(password_cdb)
    url = host + ':' + port + '/' + service_name
    url_cdb = host + ':' + port + '/' + service_name_cdb if version =='12c' else url

    # 连通性检测
    conn = False
    conn_cdb = False
    try:
        conn = cx_Oracle.connect(user, password, url)
        conn_cdb = cx_Oracle.connect(user_cdb, password_cdb, url_cdb) if  version == '12c' else conn
    except Exception, e:
        error_msg = "%s 数据库连接失败：%s" % (tags, unicode(str(e), errors='ignore'))
        db_rate_level = 'red'
        my_log.logger.error(error_msg)
        my_log.logger.info('%s：初始化oracle_db表' % tags)
        insert_sql = "insert into oracle_db_his select * from oracle_db where tags = '%s'" % tags
        tools.mysql_exec(insert_sql, '')
        delete_sql = "delete from oracle_db where tags = '%s'" % tags
        tools.mysql_exec(delete_sql, '')
        error_sql = "insert into oracle_db(tags,host,port,service_name,mon_status,rate_level) values(%s,%s,%s,%s,%s,%s)"
        value = (tags, host, port, service_name, 'connected error', db_rate_level)
        tools.mysql_exec(error_sql, value)
        # 更新数据库打分信息
        my_log.logger.info('%s :开始更新数据库评分信息' % tags)
        delete_sql = "delete from oracle_db_rate where tags= '%s'" % tags
        tools.mysql_exec(delete_sql, '')
        insert_sql = "insert into oracle_db_rate(tags,host,port,service_name,db_rate,db_rate_level,db_rate_color,db_rate_reason) select tags,host,port,service_name,'0','danger','red','connected error' from tab_oracle_servers where tags ='%s'" % tags
        tools.mysql_exec(insert_sql, '')
        my_log.logger.info('%s扣分明细，总评分:%s,扣分原因:%s' % (tags, '0', 'connected error'))
    if conn and conn_cdb:
        # 表空间监控
        my_log.logger.info('%s：开始获取Oracle数据库表空间监控信息' % tags)

        tbs = check_ora.check_tbs(conn)
        # 归档历史数据
        my_log.logger.info('%s：初始化oracle_tbs表' % tags)
        insert_sql = "insert into oracle_tbs_his select * from oracle_tbs where tags = '%s'" % tags
        tools.mysql_exec(insert_sql, '')
        delete_sql = "delete from oracle_tbs where tags = '%s' " % tags
        tools.mysql_exec(delete_sql, '')
        for line in tbs:
            if not line[6]:
                tbs_percent = 0
            else:
                tbs_percent = float(line[6])
            tbs_rate_level = tools.get_rate_level(tbs_percent)
            insert_tbs_sql = "insert into oracle_tbs(tags,host,port,service_name,tbs_name,datafile_count,size_gb,free_gb,used_gb,max_free,pct_used,pct_free,rate_level) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            value = (
                tags, host, port, service_name, line[0], line[1], line[2], line[3], line[4], line[5], line[6], line[7],
                tbs_rate_level)

            my_log.logger.info('%s：获取Oracle数据库表空间使用率(表空间名：%s 使用率：%s)' % (tags, line[0], line[6]))

            tools.mysql_exec(insert_tbs_sql, value)
        # db信息监控
        my_log.logger.info('%s：开始获取Oracle数据库监控信息' % tags)

        # 基础信息
        dbnameinfo = check_ora.get_dbname_info(conn)
        instance_info = check_ora.get_instance_info(conn)
        uptime = datetime.now() - instance_info[0][3]
        up_days = uptime.days
        process = check_ora.check_process(conn_cdb)
        asm = check_ora.check_asm(conn)
        archive_used = check_ora.get_archived(conn)
        # archive_used = None
        audit_trail = check_ora.get_para(conn, 'audit_trail')
        is_rac = check_ora.get_para(conn, 'cluster_database')
        flashback_on = dbnameinfo[0][6]

        # Oraclestat
        oraclestat = Oraclestat(conn)
        oraclestat.get_oracle_stat()
        time.sleep(1)
        oracle_data = oraclestat.get_oracle_stat()
        oracle_mem = oracle_data['mem']
        pga_size = oracle_mem['pga size']
        sga_size = oracle_mem['sga size']
        mem_pct = oracle_mem['mem pct']
        oracle_stat = oracle_data['stat']
        oracle_time = oracle_data['time']
        oracle_sess = oracle_data['sess']
        oracle_wait = oracle_data['wait']
        if not archive_used:
            archive_used_pct=''
            archive_rate_level=''
        else:
            archive_used_pct = archive_used[0][0]
            archive_rate_level = tools.get_rate_level(archive_used[0][0])
        # PGA使用率
        oracle_pga = check_ora.check_pga(conn)
        pga_target_size,pga_used_size,pga_used_pct = oracle_pga[0]
        adg_trs = check_ora.check_adg_trs(conn)
        adg_apl = check_ora.check_adg_apl(conn)
        err_info = check_ora.check_err(conn, host, user_os, password_os,ssh_port_os)
        # 后台日志入库
        log_parser.get_oracle_alert(conn, tags, host, user_os, password_os,ssh_port_os,version)
        db_rate_level = 'green'
        # 连接数评级
        conn_percent = float(process[0][3])
        conn_rate_level = tools.get_rate_level(conn_percent)
        # 归档历史数据
        my_log.logger.info('%s：初始化oracle_db表' % tags)
        insert_sql = "insert into oracle_db_his select * from oracle_db where tags = '%s'" % tags
        tools.mysql_exec(insert_sql, '')
        delete_sql = "delete from oracle_db where tags = '%s'" % tags
        tools.mysql_exec(delete_sql, '')
        # adg
        if len(adg_trs) > 0:
            # adg传输评级
            transport_value = float(adg_trs[0][1])
            # 传输延迟超过300s
            if transport_value >= 60 * 5:
                transport_rate_level = 'red'
            elif transport_value > 0 and transport_value < 60 * 5:
                transport_rate_level = 'yellow'
            else:
                transport_rate_level = 'green'
            if len(adg_apl)>0:
                apply_value = float(adg_apl[0][1])
                if apply_value >= 60 * 5:
                    apply_rate_level = 'red'
                elif apply_value > 0 and apply_value < 60 * 5:
                    apply_rate_level = 'yellow'
                else:
                    apply_rate_level = 'green'
            else:
                apply_value=0
                apply_rate_level=''


            adg_transport_lag = adg_trs[0][0]
            adg_apply_lag = adg_apl[0][0]
        else:
            transport_value = 0
            transport_rate_level = ''
            apply_value = 0
            apply_rate_level = ''
            adg_transport_lag = ''
            adg_apply_lag = ''

        insert_db_sql = "insert into oracle_db(tags,host,port,service_name,dbid,dbname,version,db_unique_name,database_role,uptime,audit_trail," \
                        "open_mode,log_mode,is_rac,flashback_on,archive_used,archive_rate_level,inst_id,instance_name,host_name,max_process,current_process,percent_process,conn_rate_level," \
                        "pga_target_size,pga_used_size,pga_used_pct,adg_" \
                        "transport_lag,adg_apply_lag,adg_transport_value,adg_transport_rate_level,adg_apply_value,adg_apply_rate_level,mon_status,err_info,sga_size,pga_size,mem_pct,qps,tps," \
                        "exec_count,user_commits,gets,logr,phyr,phyw,blockchange,redo,parse,hardparse,netin,netout,io,total_sess,act_sess,act_trans,blocked_sess,dbtime,dbcpu,log_para_wait,log_sync_wait,log_sync_cnt," \
                        "scat_wait,scat_read_cnt,seq_wait,seq_read_cnt,row_lock_cnt,rate_level)" \
                        " values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s," \
                        "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        value = (
            tags, host, port, service_name, dbnameinfo[0][5], dbnameinfo[0][0], instance_info[0][4], dbnameinfo[0][1],
            dbnameinfo[0][2], up_days, audit_trail[0][0], dbnameinfo[0][3],
            dbnameinfo[0][4], is_rac[0][0], flashback_on, archive_used_pct, archive_rate_level,
            instance_info[0][0],
            instance_info[0][1],
            instance_info[0][2], process[0][2], process[0][1], process[0][3], conn_rate_level,
            pga_target_size,pga_used_size,pga_used_pct,
            adg_transport_lag,adg_apply_lag,
            transport_value, transport_rate_level, apply_value, apply_rate_level, 'connected', err_info, sga_size,
            pga_size, mem_pct,
            oracle_stat['qps'], oracle_stat['tps'], oracle_stat['execute count'], oracle_stat['user commits'],
            oracle_stat['gets'], oracle_stat['logr'], oracle_stat['phyr'], oracle_stat['phyw'],
            oracle_stat['blockchange'], oracle_stat['redo'], oracle_stat['parse'], oracle_stat['hardparse'],
            oracle_stat['netin'], oracle_stat['netout'], oracle_stat['io_throughput'],
            oracle_sess['total'], oracle_sess['act'], oracle_sess['act_trans'], oracle_sess['blocked'],
            oracle_time['dbtime'], oracle_time['dbcpu'], oracle_wait['log_para_wait'], oracle_wait['log_sync_wait'],
            oracle_wait['log_sync_cnt'], oracle_wait['scat_wait'], oracle_wait['scat_read_cnt'],
            oracle_wait['seq_wait'], oracle_wait['seq_read_cnt'], oracle_wait['row_lock_cnt'], db_rate_level)
        tools.mysql_exec(insert_db_sql, value)
        my_log.logger.info('%s：获取Oracle数据库监控数据(数据库名：%s 数据库角色：%s 数据库状态：%s 连接数使用率：%s )' % (
            tags, dbnameinfo[0][0], dbnameinfo[0][2], dbnameinfo[0][3], process[0][3]))

        # 密码过期信息监控
        my_log.logger.info('%s：开始获取Oracle数据库用户密码过期信息' % tags)
        pwd_info = check_ora.get_pwd_info(conn)
        # 删除历史数据
        my_log.logger.info('%s：初始化oracle_expired_pwd表' % tags)
        delete_sql = "delete from oracle_expired_pwd where tags = '%s'" % tags
        tools.mysql_exec(delete_sql, '')
        for line in pwd_info:
            insert_pwd_info_sql = "insert into oracle_expired_pwd(tags,host,port,service_name,username,result_number) values(%s,%s,%s,%s,%s,%s)"
            value = (tags, host, port, service_name, line[0], line[1])
            tools.mysql_exec(insert_pwd_info_sql, value)

        # 等待事件监控
        my_log.logger.info('%s：开始获取Oracle数据库等待事件信息' % tags)

        event_info = check_ora.get_event_info(conn)
        # 归档历史数据
        my_log.logger.info('%s：初始化oracle_db_event表' % tags)
        insert_sql = "insert into oracle_db_event_his select * from oracle_db_event where tags = '%s'" % tags
        tools.mysql_exec(insert_sql, '')
        delete_sql = "delete from oracle_db_event where tags = '%s'" % tags
        tools.mysql_exec(delete_sql, '')
        for line in event_info:
            insert_event_info_sql = "insert into oracle_db_event(tags,host,port,service_name,event_no,event_name,event_cnt) values(%s,%s,%s,%s,%s,%s,%s)"
            value = (tags, host, port, service_name, line[0], line[1], line[2])
            tools.mysql_exec(insert_event_info_sql, value)

        # 锁等待监控
        my_log.logger.info('%s：开始获取Oracle数据库锁等待信息' % tags)

        lock_info = check_ora.get_lock_info(conn)
        # 删除历史数据
        my_log.logger.info('%s：初始化oracle_Lock表' % tags)
        delete_sql = "delete from oracle_lock where tags = '%s'" % tags
        tools.mysql_exec(delete_sql, '')
        for line in lock_info:
            insert_lock_info_sql = "insert into oracle_lock(tags,host,port,service_name,session,lmode,ctime,inst_id,lmode1,type,session_id) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            value = (tags, host, port, service_name, line[0], line[1], line[2], line[3], line[6], line[8], line[9])
            tools.mysql_exec(insert_lock_info_sql, value)
            my_log.logger.info('%s 获取Oracle数据库锁等待信息' % tags)

        # 无效索引监控
        my_log.logger.info('%s：开始获取Oracle数据库无效索引信息' % tags)

        invalid_index_info = check_ora.get_invalid_index(conn)
        # 删除历史数据
        my_log.logger.info('%s：初始化oracle_invalid_index表' % tags)
        delete_sql = "delete from oracle_invalid_index where tags = '%s'" % tags
        tools.mysql_exec(delete_sql, '')
        for line in invalid_index_info:
            insert_invalid_index_info_sql = "insert into oracle_invalid_index(tags,host,port,service_name,owner,index_name,partition_name,status) values(%s,%s,%s,%s,%s,%s,%s,%s)"
            value = (tags, host, port, service_name, line[0], line[1], line[2], line[3])
            tools.mysql_exec(insert_invalid_index_info_sql, value)
            my_log.logger.info('%s 获取Oracle数据库无效索引信息' % tags)

        # 临时表空间监控
        my_log.logger.info('%s：开始获取Oracle数据库临时表空间监控信息' % tags)

        tmp_tbs = check_ora.check_tmp_tbs(conn)
        # 归档历史数据
        my_log.logger.info('%s：初始化oracle_tmp_tbs表' % tags)
        insert_sql = "insert into oracle_tmp_tbs_his select * from oracle_tmp_tbs where tags = '%s'" % tags
        tools.mysql_exec(insert_sql, '')
        delete_sql = "delete from oracle_tmp_tbs where tags = '%s'" % tags
        tools.mysql_exec(delete_sql, '')
        for line in tmp_tbs:
            tmp_pct_used = float(line[3])
            tmp_rate_level = tools.get_rate_level(tmp_pct_used)
            insert_tmp_tbs_sql = "insert into oracle_tmp_tbs(tags,host,port,service_name,tmp_tbs_name,total_mb,used_mb,pct_used,rate_level) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            value = (tags, host, port, service_name, line[0], line[1], line[2], line[3], tmp_rate_level)
            tools.mysql_exec(insert_tmp_tbs_sql, value)
            my_log.logger.info('%s：获取Oracle数据库临时表空间使用率(temp表空间名：%s 使用率：%s)' % (tags, line[0], line[3]))

        # undo表空间监控
        my_log.logger.info('%s：开始获取Oracle数据库undo表空间监控信息' % tags)
        undo_tbs = check_ora.check_undo_tbs(conn)
        # 归档历史数据
        my_log.logger.info('%s：初始化oracle_undo_tbs表' % tags)
        insert_sql = "insert into oracle_undo_tbs_his select * from oracle_undo_tbs where tags = '%s'" % tags
        tools.mysql_exec(insert_sql, '')
        delete_sql = "delete from oracle_undo_tbs where tags = '%s'" % tags
        tools.mysql_exec(delete_sql, '')
        for line in undo_tbs:
            undo_pct_used = float(line[3])
            undo_rate_level = tools.get_rate_level(undo_pct_used)
            insert_undo_tbs_sql = "insert into oracle_undo_tbs(tags,host,port,service_name,undo_tbs_name,total_mb,used_mb,pct_used,rate_level) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            value = (tags, host, port, service_name, line[0], line[2], line[1], line[3], undo_rate_level)
            tools.mysql_exec(insert_undo_tbs_sql, value)
            my_log.logger.info('%s：获取Oracle数据库undo表空间使用率(undo表空间名：%s 使用率：%s)' % (tags, line[0], line[3]))

        # 更新数据库打分信息
        my_log.logger.info('%s :开始更新Oracle数据库评分信息' % tags)

        # 内存使用率扣分
        mem_stat = tools.mysql_query(
            "select host,host_name,mem_used from os_info where mem_used is not null and host = '%s'" % host)
        if mem_stat == 0:
            my_log.logger.warning('%s：内存使用率未采集到数据' % tags)
            db_mem_decute = 0
            db_mem_decute_reason = ''
        else:
            db_mem_used = float(mem_stat[0][2])

            db_mem_decute = tools.get_decute(db_mem_used)
            if db_mem_decute <> 0:
                db_mem_decute_reason = '内存使用率：%d%% \n' % db_mem_used
            else:
                db_mem_decute_reason = ''

        # cpu使用率扣分
        cpu_stat = tools.mysql_query(
            "select host,host_name,cpu_used from os_info where cpu_used is not null and host = '%s'" % host)
        if cpu_stat == 0:
            my_log.logger.warning('%s：CPU使用率未采集到数据' % tags)
            db_cpu_decute = 0
            db_cpu_decute_reason = ''
        else:
            db_cpu_used = float(cpu_stat[0][2])
            db_cpu_decute = tools.get_decute(db_cpu_used)
            if db_cpu_decute <> 0:
                db_cpu_decute_reason = 'CPU使用率：%d%% \n' % db_cpu_used
            else:
                db_cpu_decute_reason = ''

        # 连接数扣分
        process_stat = tools.mysql_query(
            "select max_process,current_process,percent_process from oracle_db where current_process is not null and tags = '%s'" % tags)
        if process_stat == 0:
            my_log.logger.warning('%s：连接数未采集到数据' % tags)
            db_conn_decute = 0
            db_conn_decute_reason = ''
        else:
            db_conn_used = float(process_stat[0][2])
            db_conn_decute = tools.get_decute(db_conn_used)
            if db_conn_decute <> 0:
                db_conn_decute_reason = '连接数：%d%% \n' % db_conn_used
            else:
                db_conn_decute_reason = ''

        # 归档使用率扣分
        archive_stat = tools.mysql_query(
            "select archive_used from oracle_db where length(archive_used) >0 and tags = '%s'" % tags)
        if archive_stat == 0 or not archive_stat:
            my_log.logger.warning('%s：归档未采集到数据' % tags)
            db_archive_decute = 0
            db_archive_decute_reason = ''
        else:
            db_archive_used = float(archive_stat[0][0])
            db_archive_decute = tools.get_decute(db_archive_used)
            if db_archive_decute <> 0:
                db_archive_decute_reason = '归档使用率：%d%% \n' % db_archive_used
            else:
                db_archive_decute_reason = ''

        # 综合性能扣分
        event_sql = ''' select tags, host, port, service_name, cnt_all from (select tags, host, port, service_name, sum(event_cnt) cnt_all
                                         from oracle_db_event_his where tags = '%s' and timestampdiff(minute, chk_time, current_timestamp()) < %s
                                         group by tags, host, port, service_name) t ''' % (tags, 10)
        event_stat = tools.mysql_query(event_sql)
        if event_stat == 0:
            my_log.logger.warning('%s：归档未采集到数据' % tags)
            db_event_decute = 0
            db_event_decute_reason = ''
        else:
            db_event_cnt = float(event_stat[0][4])
            db_event_decute = db_event_cnt / 100
            if db_event_decute <> 0:
                db_event_decute_reason = '等待事件数量：%d \n' % db_event_cnt
            else:
                db_event_decute_reason = ''

        # 表空间使用率扣分
        tbs_stat = tools.mysql_query(
            "select host,port,service_name,tbs_name,size_gb,free_gb,pct_used from oracle_tbs where tags='%s'" % tags)
        if tbs_stat == 0:
            my_log.logger.warning('%s：表空间使用率未采集到数据' % host)
            db_tbs_decute_reason = ''
            db_tbs_decute = 0
        else:
            db_tbs_decute_reason = ''
            db_tbs_decute = 0
            for each_tbs_stat in tbs_stat:
                each_tbs_name = each_tbs_stat[3]
                each_tbs_free = float(each_tbs_stat[5])
                each_tbs_used = float(each_tbs_stat[6])
                db_each_tbs_decute = tools.get_decute_tbs(each_tbs_used, each_tbs_free)
                if db_each_tbs_decute <> 0:
                    db_each_tbs_decute_reason = '%s表空间使用率：%d%% 剩余空间：%d \n' % (
                        each_tbs_name, each_tbs_used, each_tbs_free)
                else:
                    db_each_tbs_decute_reason = ''
                db_tbs_decute = max(db_tbs_decute, db_each_tbs_decute)
                db_tbs_decute_reason = db_tbs_decute_reason + db_each_tbs_decute_reason

        # 临时表空间使用率扣分
        tmp_tbs_stat = tools.mysql_query(
            "select host,port,service_name,tmp_tbs_name,total_mb,used_mb,pct_used from oracle_tmp_tbs where tags='%s'" % tags)
        if tmp_tbs_stat == 0:
            my_log.logger.warning('%s：临时表空间使用率未采集到数据' % tags)
            db_tmp_tbs_decute_reason = ''
            db_tmp_tbs_decute = 0
        else:
            db_tmp_tbs_decute_reason = ''
            db_tmp_tbs_decute = 0
            for each_tmp_tbs_stat in tmp_tbs_stat:
                each_tmp_tbs_name = each_tmp_tbs_stat[3]
                each_tmp_tbs_free = float(each_tmp_tbs_stat[4]) - float(each_tmp_tbs_stat[5])
                each_tmp_tbs_used = float(each_tmp_tbs_stat[6])
                db_each_tmp_tbs_decute = tools.get_decute_tmp_tbs(each_tmp_tbs_used, each_tmp_tbs_free)
                if db_each_tmp_tbs_decute <> 0:
                    db_each_tmp_tbs_decute_reason = '%s临时表空间使用率：%d%% 剩余空间：%d \n' % (
                        each_tmp_tbs_name, each_tmp_tbs_used, each_tmp_tbs_free)
                else:
                    db_each_tmp_tbs_decute_reason = ''
                db_tmp_tbs_decute = max(db_tmp_tbs_decute, db_each_tmp_tbs_decute)
                db_tmp_tbs_decute_reason = db_tmp_tbs_decute_reason + db_each_tmp_tbs_decute_reason

        # undo表空间使用率扣分
        undo_tbs_stat = tools.mysql_query(
            "select host,port,service_name,undo_tbs_name,total_mb,used_mb,pct_used from oracle_undo_tbs where tags='%s'" % tags)
        if undo_tbs_stat == 0:
            my_log.logger.warning('%s：undo表空间使用率未采集到数据' % tags)
            db_undo_tbs_decute_reason = ''
            db_undo_tbs_decute = 0
        else:
            db_undo_tbs_decute_reason = ''
            db_undo_tbs_decute = 0
            for each_undo_tbs_stat in undo_tbs_stat:
                each_undo_tbs_name = each_undo_tbs_stat[3]
                each_undo_tbs_free = float(each_undo_tbs_stat[4]) - float(each_undo_tbs_stat[5])
                each_undo_tbs_used = float(each_undo_tbs_stat[6])
                db_each_undo_tbs_decute = tools.get_decute_undo_tbs(each_undo_tbs_used, each_undo_tbs_free)
                if db_each_undo_tbs_decute <> 0:
                    db_each_undo_tbs_decute_reason = "'%s'undo表空间使用率：'%d'%% 剩余空间：%d \n" % (
                        each_undo_tbs_name, each_undo_tbs_used, each_undo_tbs_free)
                else:
                    db_each_undo_tbs_decute_reason = ''
                db_undo_tbs_decute = max(db_undo_tbs_decute, db_each_undo_tbs_decute)
                db_undo_tbs_decute_reason = db_undo_tbs_decute_reason + db_each_undo_tbs_decute_reason

        db_top_decute = max(db_conn_decute, db_archive_decute, db_event_decute, db_tbs_decute, db_cpu_decute,
                            db_mem_decute,
                            db_tmp_tbs_decute, db_undo_tbs_decute)
        db_all_rate = 100 - db_top_decute
        if db_all_rate >= 60:
            db_rate_color = 'green'
            db_rate_level = 'success'
        elif db_all_rate >= 20 and db_all_rate < 60:
            db_rate_color = 'yellow'
            db_rate_level = 'warning'
        else:
            db_rate_color = 'red'
            db_rate_level = 'danger'
        db_all_decute_reason = db_conn_decute_reason + db_archive_decute_reason + db_event_decute_reason + db_tbs_decute_reason + db_cpu_decute_reason + db_mem_decute_reason + db_tmp_tbs_decute_reason + db_undo_tbs_decute_reason

        delete_sql = "delete from oracle_db_rate where tags= '%s'" % tags
        tools.mysql_exec(delete_sql, '')

        # 插入总评分及扣分明细
        insert_sql = "insert into oracle_db_rate(tags,host,port,service_name,conn_decute,archive_decute,event_decute,tbs_decute,tmp_decute,undo_decute,cpu_decute,mem_decute,db_rate,db_rate_level,db_rate_color,db_rate_reason) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        value = (
            tags, host, port, service_name, db_conn_decute, db_archive_decute, db_event_decute, db_tbs_decute,
            db_tmp_tbs_decute, db_undo_tbs_decute, db_cpu_decute, db_mem_decute, db_all_rate,
            db_rate_level, db_rate_color, db_all_decute_reason)
        tools.mysql_exec(insert_sql, value)
        my_log.logger.info(
            '%s扣分明细，连接数扣分:%s，归档使用率扣分：%s, 等待事件扣分：%s, 表空间扣分:%s，临时表空间扣分:%s,Undo表空间扣分:%s,cpu使用率扣分:%s，内存使用率扣分:%s，总评分:%s,扣分原因:%s' % (
                tags, db_conn_decute, db_archive_decute_reason, db_event_decute_reason, db_tbs_decute,
                db_tmp_tbs_decute,
                db_undo_tbs_decute, db_cpu_decute, db_mem_decute, db_all_rate, db_all_decute_reason))


def check_mysql(tags, host,port,user,password,user_os,password_os):
    my_log.logger.info('等待2秒待Linux主机信息采集完毕')
    password = base64.decodestring(password)
    password_os = base64.decodestring(password_os)
    # 连通性检测
    conn = False
    try:
        conn = MySQLdb.connect(host=host, user=user, passwd=password, port=int(port), connect_timeout=5, charset='utf8')
    except Exception, e:
        error_msg = "%s mysql数据库连接失败：%s" % (tags, unicode(str(e), errors='ignore'))
        db_rate_level = 'red'
        my_log.logger.error(error_msg)
        my_log.logger.info('%s：初始化mysql_db表' % tags)
        insert_sql = "insert into mysql_db_his select * from mysql_db where tags = '%s'" % tags
        tools.mysql_exec(insert_sql, '')
        delete_sql = "delete from mysql_db where tags = '%s'" % tags
        tools.mysql_exec(delete_sql, '')
        error_sql = "insert into mysql_db(host,port,tags,mon_status,rate_level) values(%s,%s,%s,%s,%s)"
        value = (host, port, tags, 'connected error', db_rate_level)
        tools.mysql_exec(error_sql, value)
        # 更新数据库打分信息
        my_log.logger.info('%s :开始更新数据库评分信息' % tags)
        delete_sql = "delete from mysql_db_rate where tags= '%s'" % tags
        tools.mysql_exec(delete_sql, '')
        insert_sql = "insert into mysql_db_rate(host,port,tags,db_rate,db_rate_level,db_rate_color,db_rate_reason) select host,port,tags,'0','danger','red','connected error' from tab_mysql_servers where tags ='%s'" % tags
        tools.mysql_exec(insert_sql, '')
        my_log.logger.info('%s扣分明细，总评分:%s,扣分原因:%s' % (tags, '0', 'conected error'))
    if conn:
        my_log.logger.info('%s：开始获取mysql数据库监控信息' % tags)

        db_rate_level = 'green'
        # 获取两次状态值
        my_log.logger.info('%s：获取第一次MySQL状态采样' % tags)
        mysql_stat = check_msql.get_mysql_status(conn)
        time.sleep(1)
        my_log.logger.info('%s：获取第二次MySQL状态采样' % tags)
        mysql_stat_next = check_msql.get_mysql_status(conn)

        # 基础信息
        mysql_version = check_msql.get_mysql_para(conn, 'version')
        mysql_uptime = float(mysql_stat['Uptime']) / 86400
        mysql_datadir = check_msql.get_mysql_para(conn, 'datadir')
        mysql_slow_query = check_msql.get_mysql_para(conn, 'slow_query_log')
        mysql_binlog = check_msql.get_mysql_para(conn, 'log_bin')

        # 后台日志
        log_parser.get_mysql_alert(conn, tags, host, user_os, password_os)

        # 连接信息
        mysql_max_connections = check_msql.get_mysql_para(conn, 'max_connections')
        current_conn = mysql_stat['Threads_connected']
        threads_running = mysql_stat['Threads_running']
        threads_created = mysql_stat['Threads_created']
        threads_cached = mysql_stat['Threads_cached']
        threads_waited = int(check_msql.get_mysql_waits(conn))
        max_connect_errors = check_msql.get_mysql_para(conn, 'max_connect_errors')
        mysql_conn_rate = "%2.2f" % (float(current_conn) / float(mysql_max_connections))

        # _buffer_size
        key_buffer_size = float(check_msql.get_mysql_para(conn, 'key_buffer_size')) / 1024 / 1024
        sort_buffer_size = float(check_msql.get_mysql_para(conn, 'sort_buffer_size')) / 1024
        join_buffer_size = float(check_msql.get_mysql_para(conn, 'join_buffer_size')) / 1024

        # _blocks_unused
        key_blocks_unused = mysql_stat['Key_blocks_unused']
        key_blocks_used = mysql_stat['Key_blocks_used']
        key_blocks_not_flushed = mysql_stat['Key_blocks_not_flushed']

        key_blocks_used_rate = "%2.2f" % (float(key_blocks_used) / (float(key_blocks_used) + float(key_blocks_unused)))
        if float(mysql_stat['Key_read_requests']) <> 0:
            key_buffer_read_rate = "%2.2f" % (
                    float(mysql_stat['Key_reads']) / float(mysql_stat['Key_read_requests']))
        else:
            key_buffer_read_rate = 0
        if float(mysql_stat['Key_write_requests']) <> 0:
            key_buffer_write_rate = "%2.2f" % (
                    float(mysql_stat['Key_writes']) / float(mysql_stat['Key_write_requests']))
        else:
            key_buffer_write_rate = 0

        # 打开文件数
        open_files_limit = check_msql.get_mysql_para(conn, 'open_files_limit')
        open_files = mysql_stat['Open_files']

        # 表缓存数，已打开表
        table_open_cache = check_msql.get_mysql_para(conn, 'table_open_cache')
        open_tables = mysql_stat['Open_tables']

        # QPS,TPS
        mysql_qps = int(mysql_stat_next['Questions']) - int(mysql_stat['Questions'])
        mysql_tps = int(mysql_stat_next['Com_commit']) + int(mysql_stat_next['Com_rollback']) - (
                int(mysql_stat['Com_commit']) + int(mysql_stat['Com_rollback']))

        # sql执行情况
        mysql_sel = int(mysql_stat_next['Com_select']) - int(mysql_stat['Com_select'])
        mysql_ins = int(mysql_stat_next['Com_insert']) - int(mysql_stat['Com_insert'])
        mysql_upd = int(mysql_stat_next['Com_update']) - int(mysql_stat['Com_update'])
        mysql_del = int(mysql_stat_next['Com_delete']) - int(mysql_stat['Com_delete'])

        # 全表扫描数
        select_scan = int(mysql_stat_next['Select_scan']) - int(mysql_stat['Select_scan'])

        # 慢查询数量
        slow_queries = int(mysql_stat_next['Slow_queries']) - int(mysql_stat['Slow_queries'])

        # myisam读写次数
        key_read_requests = int(mysql_stat_next['Key_read_requests']) - int(mysql_stat['Key_read_requests'])
        key_reads = int(mysql_stat_next['Key_reads']) - int(mysql_stat['Key_reads'])
        key_write_requests = int(mysql_stat_next['Key_write_requests']) - int(mysql_stat['Key_write_requests'])
        Key_writes = int(mysql_stat_next['Key_writes']) - int(mysql_stat['Key_writes'])

        # 流量
        mysql_bytes_received = (int(mysql_stat_next['Bytes_received']) - int(mysql_stat['Bytes_received'])) / 1024
        mysql_bytes_sent = (int(mysql_stat_next['Bytes_sent']) - int(mysql_stat['Bytes_sent'])) / 1024

        # innodb
        # innodb_buffer_pool
        innodb_buffer_pool_size = int(check_msql.get_mysql_para(conn, 'innodb_buffer_pool_size')) / 1024 / 1024
        innodb_buffer_pool_pages_total = mysql_stat['Innodb_buffer_pool_pages_total']
        innodb_buffer_pool_pages_data = mysql_stat['Innodb_buffer_pool_pages_data']
        innodb_buffer_pool_pages_dirty = mysql_stat['Innodb_buffer_pool_pages_dirty']
        innodb_buffer_pool_pages_flushed = mysql_stat['Innodb_buffer_pool_pages_flushed']
        innodb_buffer_pool_pages_free = mysql_stat['Innodb_buffer_pool_pages_free']

        # innodb缓冲区命中率
        innodb_buffer_pool_reads_requests = int(mysql_stat_next['Innodb_buffer_pool_read_requests']) - int(
            mysql_stat['Innodb_buffer_pool_read_requests'])
        innodb_buffer_pool_reads = int(mysql_stat_next['Innodb_buffer_pool_reads']) - int(
            mysql_stat['Innodb_buffer_pool_reads'])
        if innodb_buffer_pool_reads_requests == 0:
            innodb_buffer_pool_hit = 100
        else:
            innodb_buffer_pool_hit = (1 - innodb_buffer_pool_reads / innodb_buffer_pool_reads_requests) * 100

        # innodb缓冲区使用率
        innodb_buffer_usage = (1 - int(innodb_buffer_pool_pages_free) / int(innodb_buffer_pool_pages_total)) * 100
        # innodb缓冲区脏块率
        innodb_buffer_dirty_rate = (int(innodb_buffer_pool_pages_dirty) / int(innodb_buffer_pool_pages_total)) * 100

        # io
        innodb_io_capacity = check_msql.get_mysql_para(conn, 'innodb_io_capacity')
        innodb_read_io_threads = check_msql.get_mysql_para(conn, 'innodb_read_io_threads')
        innodb_write_io_threads = check_msql.get_mysql_para(conn, 'innodb_write_io_threads')

        # innodb_rows
        innodb_rows_deleted_persecond = int(mysql_stat_next['Innodb_rows_deleted']) - int(
            mysql_stat['Innodb_rows_deleted'])
        innodb_rows_inserted_persecond = int(mysql_stat_next['Innodb_rows_inserted']) - int(
            mysql_stat['Innodb_rows_inserted'])
        innodb_rows_read_persecond = int(mysql_stat_next['Innodb_rows_read']) - int(mysql_stat['Innodb_rows_read'])
        innodb_rows_updated_persecond = int(mysql_stat_next['Innodb_rows_updated']) - int(
            mysql_stat['Innodb_rows_updated'])

        # innodb锁等待
        innodb_row_lock_waits = int(mysql_stat_next['Innodb_row_lock_waits']) - int(mysql_stat['Innodb_row_lock_waits'])
        innodb_row_lock_time_avg = float(mysql_stat['Innodb_row_lock_time_avg'])

        # innodb脏页刷新频率
        innodb_buffer_pool_pages_flushed_delta = int(mysql_stat_next['Innodb_buffer_pool_pages_flushed']) - int(
            mysql_stat['Innodb_buffer_pool_pages_flushed'])

        # innodb读写量
        innodb_data_read = (int(mysql_stat_next['Innodb_data_read']) - int(mysql_stat['Innodb_data_read'])) / 1024
        innodb_data_written = (int(mysql_stat_next['Innodb_data_written']) - int(
            mysql_stat['Innodb_data_written'])) / 1024

        # innodb读写次数
        innodb_data_reads = int(mysql_stat_next['Innodb_data_reads']) - int(mysql_stat['Innodb_data_reads'])
        innodb_data_writes = int(mysql_stat_next['Innodb_data_writes']) - int(mysql_stat['Innodb_data_writes'])

        # innodb日志写出次数，日志写出量
        innodb_log_writes = int(mysql_stat_next['Innodb_log_writes']) - int(mysql_stat['Innodb_log_writes'])
        innodb_os_log_written = (int(mysql_stat_next['Innodb_os_log_written']) - int(
            mysql_stat['Innodb_os_log_written'])) / 1024

        # big_table
        mysql_big_table_list = check_msql.get_mysql_big_table(conn)

        my_log.logger.info('%s：初始化mysql_big_table表' % tags)
        insert_sql = "insert into mysql_big_table_his select * from mysql_big_table where tags = '%s'" % tags
        tools.mysql_exec(insert_sql, '')
        delete_sql = "delete from mysql_big_table where tags = '%s'" % tags
        tools.mysql_exec(delete_sql, '')

        if mysql_big_table_list:
            for mysql_big_table in mysql_big_table_list:
                table_size = mysql_big_table[2]
                if table_size:
                    table_size = float(table_size.encode('utf-8'))
                    if table_size >= 5:
                        sql = "insert into mysql_big_table(host,tags,db,table_name,total,table_comment) values('%s','%s','%s','%s',%s,'%s')" % (
                            host, tags, mysql_big_table[0], mysql_big_table[1], table_size, mysql_big_table[3])
                        tools.mysql_exec(sql, '')

        # 连接数评级
        conn_rate_level = tools.get_rate_level(float(mysql_conn_rate))

        # 归档历史监控数据
        my_log.logger.info('%s：初始化mysql_db表' % tags)
        insert_sql = "insert into mysql_db_his select * from mysql_db where tags = '%s'" % tags
        tools.mysql_exec(insert_sql, '')
        delete_sql = "delete from mysql_db where tags = '%s'" % tags
        tools.mysql_exec(delete_sql, '')

        insert_db_sql = "insert into mysql_db(host,port,tags,version,uptime,mysql_datadir,mysql_slow_query,mysql_binlog,max_connections,max_connect_errors,threads_connected,threads_running,threads_created,threads_cached,threads_waited," \
                        "conn_rate,conn_rate_level,QPS,TPS,bytes_received,bytes_send,open_files_limit,open_files,table_open_cache,open_tables," \
                        "key_buffer_size,sort_buffer_size,join_buffer_size,key_blocks_unused,key_blocks_used,key_blocks_not_flushed," \
                        "key_blocks_used_rate,key_buffer_read_rate,key_buffer_write_rate," \
                        "mysql_sel,mysql_ins,mysql_upd,mysql_del,select_scan,slow_queries,key_read_requests,key_reads,key_write_requests,Key_writes," \
                        "innodb_buffer_pool_size,innodb_buffer_pool_pages_total,innodb_buffer_pool_pages_data," \
                        "innodb_buffer_pool_pages_dirty,innodb_buffer_pool_pages_flushed,innodb_buffer_pool_pages_free,innodb_buffer_pool_hit,innodb_buffer_usage,innodb_buffer_dirty_rate," \
                        "innodb_io_capacity,innodb_read_io_threads,innodb_write_io_threads," \
                        "innodb_rows_deleted_persecond,innodb_rows_inserted_persecond,innodb_rows_read_persecond,innodb_rows_updated_persecond," \
                        "innodb_row_lock_waits,innodb_row_lock_time_avg,innodb_buffer_pool_pages_flushed_delta,innodb_data_read,innodb_data_written,innodb_data_reads,innodb_data_writes,innodb_log_writes,innodb_os_log_written," \
                        "mon_status,rate_level) " \
                        "values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s," \
                        "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        value = (
            host, port, tags, mysql_version, mysql_uptime, mysql_datadir, mysql_slow_query, mysql_binlog,
            mysql_max_connections,
            max_connect_errors, current_conn,
            threads_running,
            threads_created, threads_cached, threads_waited, mysql_conn_rate,
            conn_rate_level, mysql_qps, mysql_tps, mysql_bytes_received, mysql_bytes_sent, open_files_limit,
            open_files, table_open_cache, open_tables,
            key_buffer_size, sort_buffer_size, join_buffer_size, key_blocks_unused, key_blocks_used,
            key_blocks_not_flushed,
            float(key_blocks_used_rate) * 100, float(key_buffer_read_rate) * 100,
            float(key_buffer_write_rate) * 100, mysql_sel, mysql_ins, mysql_upd, mysql_del, select_scan,
            slow_queries,
            key_read_requests, key_reads, key_write_requests, Key_writes,
            innodb_buffer_pool_size, innodb_buffer_pool_pages_total, innodb_buffer_pool_pages_data,
            innodb_buffer_pool_pages_dirty, innodb_buffer_pool_pages_flushed, innodb_buffer_pool_pages_free,
            innodb_buffer_pool_hit, innodb_buffer_usage, innodb_buffer_pool_pages_dirty,
            innodb_io_capacity, innodb_read_io_threads, innodb_write_io_threads, innodb_rows_deleted_persecond,
            innodb_rows_inserted_persecond, innodb_rows_read_persecond, innodb_rows_updated_persecond,
            innodb_row_lock_waits, innodb_row_lock_time_avg, innodb_buffer_pool_pages_flushed_delta,
            innodb_data_read, innodb_data_written, innodb_data_reads, innodb_data_writes, innodb_log_writes,
            innodb_os_log_written,
            'connected', 'green')
        tools.mysql_exec(insert_db_sql, value)
        my_log.logger.info('%s：获取Mysql数据库监控数据(IP：%s 端口号：%s 连接使用率：%s 连接状态：%s )' % (
            tags, host, port, mysql_conn_rate, 'connected'))

        # 复制
        server_id = check_msql.get_mysql_para(conn, 'server_id')
        is_slave = ''
        is_master = ''
        read_only_result = ''
        master_server = ''
        master_port = ''
        slave_io_run = ''
        slave_io_rate = ''
        slave_sql_run = ''
        slave_sql_rate = ''
        delay = '-'
        delay_rate = ''
        current_binlog_file = ''
        current_binlog_pos = ''
        master_binlog_file = ''
        master_binlog_pos = ''
        master_binlog_space = ''
        curs = conn.cursor()
        master_thread = curs.execute("select * from information_schema.processlist where COMMAND = 'Binlog Dump'")
        slave_stats = curs.execute('show slave status;')
        # 判断Mysql角色
        if master_thread:
            is_master = 'YES'
        if slave_stats:
            is_slave = 'YES'
        mysql_role = ''
        if is_master == 'YES' and is_slave <> 'YES':
            mysql_role = 'master'
        if is_master <> 'YES' and is_slave == 'YES':
            mysql_role = 'slave'
        if is_master == 'YES' and is_slave == 'YES':
            mysql_role = 'master/slave'
        if slave_stats:
            read_only = curs.execute(
                "select * from information_schema.global_variables where variable_name='read_only';")
            read_only_query = curs.fetchone()
            read_only_result = read_only_query[1]
            slave_info = curs.execute("show slave status;")
            slave_result = curs.fetchone()
            master_server = slave_result[1]
            master_port = slave_result[3]
            slave_io_run = slave_result[10]
            if slave_io_run == 'Yes':
                slave_io_rate = 'green'
            else:
                slave_io_rate = 'red'
            slave_sql_run = slave_result[11]
            if slave_sql_run == 'Yes':
                slave_sql_rate = 'green'
            else:
                slave_sql_rate = 'red'
            delay = slave_result[32]

            if delay is None:
                delay_rate = 'red'
            else:
                if int(delay) == 0:
                    delay_rate = 'green'
                elif int(delay) > 0 and int(delay) < 300:
                    delay_rate = 'yellow'
                else:
                    delay_rate = 'red'

            current_binlog_file = slave_result[9]
            current_binlog_pos = slave_result[21]
            master_binlog_file = slave_result[5]
            master_binlog_pos = slave_result[6]
        elif master_thread:
            read_only = curs.execute(
                "select * from information_schema.global_variables where variable_name='read_only';")
            read_only_query = curs.fetchone()
            read_only_result = read_only_query[1]
            master_info = curs.execute('show master status;')
            master_result = curs.fetchone()
            master_binlog_file = master_result[0]
            master_binlog_pos = master_result[1]
        if master_thread:
            binlog_file = curs.execute('show master logs;')
            binlogs = 0
            if binlog_file:
                for row in curs.fetchall():
                    binlogs = binlogs + row[1]
            master_binlog_space = int(binlogs) / 1024 / 1024

        # 初始化mysql_repl表
        my_log.logger.info('%s：初始化mysql_repl表' % tags)
        insert_sql = "insert into mysql_repl_his select * from mysql_repl where tags = '%s'" % tags
        tools.mysql_exec(insert_sql, '')
        delete_sql = "delete from mysql_repl where tags = '%s'" % tags
        tools.mysql_exec(delete_sql, '')

        insert_repl_sql = "insert into mysql_repl(tags,server_id,host,port,is_master,is_slave,mysql_role,read_only,master_server,master_port,slave_io_run,slave_io_rate,slave_sql_run,slave_sql_rate,delay,delay_rate,current_binlog_file,current_binlog_pos,master_binlog_file,master_binlog_pos,master_binlog_space) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        value = (
            tags, server_id, host, port, is_master, is_slave, mysql_role, read_only_result, master_server, master_port,
            slave_io_run, slave_io_rate, slave_sql_run, slave_sql_rate, delay, delay_rate, current_binlog_file,
            current_binlog_pos, master_binlog_file, master_binlog_pos, master_binlog_space)
        tools.mysql_exec(insert_repl_sql, value)
        my_log.logger.info('%s：获取Mysql数据库复制数据' % tags)

        # 更新数据库打分信息
        my_log.logger.info('%s :开始更新Mysql数据库评分信息' % tags)

        # 内存使用率扣分
        db_mem_decute = 0
        db_mem_decute_reason = ''
        mem_stat = tools.mysql_query(
            "select host,host_name,mem_used from os_info where mem_used is not null and host = '%s'" % host)
        if mem_stat == 0:
            my_log.logger.warning('%s：内存使用率未采集到数据' % host)
            db_mem_decute = 0
        else:
            db_mem_used = float(mem_stat[0][2])
            db_mem_decute = tools.get_decute(db_mem_used)
            if db_mem_decute <> 0:
                db_mem_decute_reason = '内存使用率：%d%% \n' % db_mem_used
            else:
                db_mem_decute_reason = ''

        # cpu使用率扣分
        db_cpu_decute_reason = ''
        cpu_stat = tools.mysql_query(
            "select host,host_name,cpu_used from os_info where cpu_used is not null and host = '%s'" % host)
        if cpu_stat == 0:
            my_log.logger.warning('%s：CPU使用率未采集到数据' % host)
            db_cpu_decute = 0
        else:
            db_cpu_used = float(cpu_stat[0][2])
            db_cpu_decute = tools.get_decute(db_cpu_used)
            if db_cpu_decute <> 0:
                db_cpu_decute_reason = 'CPU使用率：%d%% \n' % db_cpu_used
            else:
                db_cpu_decute_reason = ''

        # 连接数扣分
        db_conn_decute = 0
        db_conn_decute_reason = ''
        db_conn_decute = tools.get_decute(float(mysql_conn_rate))
        if db_conn_decute <> 0:
            db_conn_decute_reason = '连接数：%d%% \n' % mysql_conn_rate
        else:
            db_conn_decute_reason = ''

        db_top_decute = max(db_conn_decute, db_cpu_decute, db_mem_decute)
        db_all_rate = 100 - db_top_decute
        if db_all_rate >= 60:
            db_rate_color = 'green'
            db_rate_level = 'success'
        elif db_all_rate >= 20 and db_all_rate < 60:
            db_rate_color = 'yellow'
            db_rate_level = 'warning'
        else:
            db_rate_color = 'red'
            db_rate_level = 'danger'
        db_all_decute_reason = db_conn_decute_reason + db_cpu_decute_reason + db_mem_decute_reason

        delete_sql = "delete from mysql_db_rate where tags= '%s'" % tags
        tools.mysql_exec(delete_sql, '')

        # 插入总评分及扣分明细
        insert_sql = "insert into mysql_db_rate(host,port,tags,conn_decute,cpu_decute,mem_decute,db_rate,db_rate_level,db_rate_color,db_rate_reason) select host,port,tags,'%s','%s','%s','%s','%s','%s','%s' from tab_mysql_servers where tags ='%s'" % (
            db_conn_decute, db_cpu_decute, db_mem_decute, db_all_rate, db_rate_level, db_rate_color,
            db_all_decute_reason, tags)
        tools.mysql_exec(insert_sql, '')
        my_log.logger.info('%s扣分明细，连接数扣分:%s，cpu使用率扣分:%s，内存使用率扣分:%s，总评分:%s,扣分原因:%s' % (
            tags, db_conn_decute, db_cpu_decute, db_mem_decute, db_all_rate, db_all_decute_reason))

def check_redis(tags, host,port):
    # 连通性检测
    info = False
    try:
        conn = Rds.StrictRedis(host=host, port=port)
        info = conn.info()
    except Exception, e:
        error_msg = "%s redis连接失败：%s" % (tags, unicode(str(e), errors='ignore'))
        redis_rate_level = 'red'
        my_log.logger.error(error_msg)
        my_log.logger.info('%s：初始化redis表' % tags)
        insert_sql = "insert into redis_his select * from redis where tags = '%s'" % tags
        tools.mysql_exec(insert_sql, '')
        delete_sql = "delete from redis where tags = '%s'" % tags
        tools.mysql_exec(delete_sql, '')
        error_sql = "insert into redis(host,port,tags,mon_status,rate_level) values(%s,%s,%s,%s,%s)"
        value = (host, port, tags, 'connected error', redis_rate_level)
        tools.mysql_exec(error_sql, value)
        my_log.logger.info('%s扣分明细，总评分:%s,扣分原因:%s' % (tags, '0', 'conected error'))
    if info:
        my_log.logger.info('%s：开始获取redis监控信息' % tags)
        redis_stats = Redisstat(conn)
        redis_data = redis_stats.get_redis_data()
        redis_info = redis_data['info']
        redis_stat = redis_data['stat']
        redis_mon_conf = redis_data['config']

        max_memory = float(redis_mon_conf['maxmemory'])
        if max_memory == 0:
            used_memory_pct = 0
        else:
            used_memory_pct = round(float(redis_info['used_memory'])/max_memory,2)

        # 归档历史数据
        my_log.logger.info('%s：初始化redis表' % tags)
        insert_sql = "insert into redis_his select * from redis where tags = '%s'" % tags
        tools.mysql_exec(insert_sql, '')
        delete_sql = "delete from redis where tags = '%s' " % tags
        tools.mysql_exec(delete_sql, '')

        insert_sql = "insert into redis(tags,host,port,version,updays,redis_mode,slaves,connection_clients,role,used_memory,mem_fragmentation_ratio,total_keys,max_memory,used_memory_pct,misses,hits,mon_status,rate_level) " \
                     "values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        values = (
            tags,host,port,redis_info['redis_version'],redis_info['uptime_in_days'],redis_info['redis_mode'],redis_info['connected_slaves'],redis_info['connected_clients'],redis_info['role'],
            round(redis_info['used_memory']/1024/1024,2),round(redis_info['used_memory_rss']/redis_info['used_memory'],2),redis_stat['total_keys'],round(max_memory/1024/1024,2),used_memory_pct,
            redis_info['keyspace_hits'],redis_info['keyspace_misses'],
            'connected','green'
        )
        tools.mysql_exec(insert_sql,values)


def check_web(tags, url):
    # 初始化表
    my_log.logger.info('%s：初始化web_url_stats表' % tags)
    insert_sql = "insert into web_url_stats_his select * from web_url_stats where tags = '%s'" % tags
    tools.mysql_exec(insert_sql, '')
    delete_sql = "delete from web_url_stats where tags = '%s'" % tags
    tools.mysql_exec(delete_sql, '')
    web_stats = web_check.http_check(url)
    res = web_stats['res']
    status_code = web_stats['status_code']
    reason = web_stats['reason']
    tim = web_stats['tim']
    insert_sql = 'insert into web_url_stats(tags,url,res,status_code,reason,tim) values(%s,%s,%s,%s,%s,%s)'
    value = (tags,url,res,status_code,reason,tim)
    tools.mysql_exec(insert_sql,value)

def check_tcp(tags, ip, port):
    # 初始化表
    my_log.logger.info('%s：初始化tcp_stats表' % tags)
    insert_sql = "insert into tcp_stats_his select * from tcp_stats where tags = '%s'" % tags
    tools.mysql_exec(insert_sql, '')
    delete_sql = "delete from tcp_stats where tags = '%s'" % tags
    tools.mysql_exec(delete_sql, '')
    tcp_stats = web_check.tcp_check(ip,port)
    res = tcp_stats['res']
    sta = tcp_stats['sta']
    tim = tcp_stats['tim']
    insert_sql = 'insert into tcp_stats(tags,ip,port,res,sta,tim) values(%s,%s,%s,%s,%s,%s)'
    value = (tags,ip,port,res,sta,tim)
    tools.mysql_exec(insert_sql,value)



if __name__ =='__main__':
    while True:
        # 读取配置文件，采集周期
        conf = ConfigParser.ConfigParser()
        conf_path = os.path.dirname(os.getcwd())
        conf.read('%s/config/db_monitor.conf' %conf_path)
        check_sleep_time = float(conf.get("policy", "check_sleep_time"))

        # 清理不在配置表中的无效数据
        linux_clr_list = ['os_info','os_filesystem','linux_rate']
        oracle_clr_list = ['oracle_tbs','oracle_db','oracle_db_event','oracle_tmp_tbs','oracle_undo_tbs','oracle_db_rate','oracle_invalid_index','oracle_expired_pwd']
        mysql_clr_list =  ['mysql_db','mysql_db_rate','mysql_repl']
        redis_clr_list = ['redis']
        url_clr_list = ['web_url_stats']
        tcp_clr_list = ['tcp_stats']

        for table in linux_clr_list:
            # 清空无效监控数据
            my_log.logger.info('清除%s表无效监控数据' %table)
            insert_sql = "insert into %s_his select * from %s where tags not in (select tags from tab_linux_servers)" %(table,table)
            tools.mysql_exec(insert_sql, '')
            delete_sql = "delete from %s where tags not in (select tags from tab_linux_servers)" %table
            tools.mysql_exec(delete_sql, '')

        for table in oracle_clr_list:
            # 清空无效监控数据
            my_log.logger.info('清除%s表无效监控数据' %table)
            insert_sql = "insert into %s_his select * from %s where tags not in (select tags from tab_oracle_servers)" %(table,table)
            tools.mysql_exec(insert_sql, '')
            delete_sql = "delete from %s where tags not in (select tags from tab_oracle_servers)" %table
            tools.mysql_exec(delete_sql, '')

        for table in mysql_clr_list:
            # 清空无效监控数据
            my_log.logger.info('清除%s表无效监控数据' %table)
            insert_sql = "insert into %s_his select * from %s where tags not in (select tags from tab_mysql_servers)" %(table,table)
            tools.mysql_exec(insert_sql, '')
            delete_sql = "delete from %s where tags not in (select tags from tab_mysql_servers)" %table
            tools.mysql_exec(delete_sql, '')

        for table in redis_clr_list:
            # 清空无效监控数据
            my_log.logger.info('清除%s表无效监控数据' %table)
            insert_sql = "insert into %s_his select * from %s where tags not in (select tags from redis_mon_conf)" %(table,table)
            tools.mysql_exec(insert_sql, '')
            delete_sql = "delete from %s where tags not in (select tags from redis_mon_conf)" %table
            tools.mysql_exec(delete_sql, '')

        for table in url_clr_list:
            # 清空无效监控数据
            my_log.logger.info('清除%s表无效监控数据' %table)
            insert_sql = "insert into %s_his select * from %s where tags not in (select tags from tab_url_conf)" %(table,table)
            tools.mysql_exec(insert_sql, '')
            delete_sql = "delete from %s where tags not in (select tags from tab_url_conf)" %table
            tools.mysql_exec(delete_sql, '')

        for table in tcp_clr_list:
            # 清空无效监控数据
            my_log.logger.info('清除%s表无效监控数据' %table)
            insert_sql = "insert into %s_his select * from %s where tags not in (select tags from tab_tcp_conf)" %(table,table)
            tools.mysql_exec(insert_sql, '')
            delete_sql = "delete from %s where tags not in (select tags from tab_tcp_conf)" %table
            tools.mysql_exec(delete_sql, '')


        # 采集设备
        linux_servers = tools.mysql_query('select tags,host,host_name,user,password,ssh_port from tab_linux_servers')
        oracle_servers = tools.mysql_query(
            'select tags,host,port,service_name,user,password,user_cdb,password_cdb,service_name_cdb,user_os,password_os,ssh_port_os,version from tab_oracle_servers')
        mysql_servers = tools.mysql_query(
            'select tags,host,port,user,password,user_os,password_os from tab_mysql_servers')
        redis_list = tools.mysql_query(
            'select tags,host,port from redis_mon_conf')
        url_list = tools.mysql_query(
            'select tags,url from tab_url_conf')
        tcp_list = tools.mysql_query(
            'select tags,ip,port from tab_tcp_conf')

        p_pool = []
        if linux_servers:
            for i in xrange(len(linux_servers)):
                l_server = Process(target=check_linux, args=(
                    linux_servers[i][0], linux_servers[i][1], linux_servers[i][2], linux_servers[i][3],linux_servers[i][4],linux_servers[i][5]))
                l_server.start()
                my_log.logger.info('%s 开始采集Linux主机信息' %linux_servers[i][0])
                p_pool.append(l_server)
        if oracle_servers:
            for i in xrange(len(oracle_servers)):
                o_server = Process(target=check_oracle, args=(
                    oracle_servers[i][0], oracle_servers[i][1], oracle_servers[i][2], oracle_servers[i][3],
                    oracle_servers[i][4], oracle_servers[i][5], oracle_servers[i][6],oracle_servers[i][7],
                    oracle_servers[i][8],oracle_servers[i][9],oracle_servers[i][10],oracle_servers[i][11],oracle_servers[i][12]))
                o_server.start()
                my_log.logger.info('%s 开始采集oracle数据库信息' %oracle_servers[i][0])
                p_pool.append(o_server)
        if mysql_servers:
            for i in xrange(len(mysql_servers)):
                m_server = Process(target=check_mysql, args=(
                    mysql_servers[i][0], mysql_servers[i][1], mysql_servers[i][2], mysql_servers[i][3],
                    mysql_servers[i][4],mysql_servers[i][5],mysql_servers[i][6]))
                m_server.start()
                my_log.logger.info('%s 开始采集mysql数据库信息' %mysql_servers[i][0])
                p_pool.append(m_server)
        if redis_list:
            for redis in redis_list:
                redis_check = Process(target=check_redis, args=(
                    redis[0],redis[1],redis[2] ))
                redis_check.start()
                my_log.logger.info('%s 开始采集redis信息' %redis[0])
                p_pool.append(redis_check)
        if url_list:
            for i in xrange(len(url_list)):
                url = Process(target=check_web, args=(url_list[i][0], url_list[i][1]))
                url.start()
                my_log.logger.info('%s 开始采集web信息' %url_list[i][0])
                p_pool.append(url)
        if tcp_list:
            for i in xrange(len(tcp_list)):
                tcp = Process(target=check_tcp, args=(tcp_list[i][0], tcp_list[i][1],tcp_list[i][2]))
                tcp.start()
                my_log.logger.info('%s 开始采集tcp信息' %tcp_list[i][0])
                p_pool.append(tcp)

        for each_server in p_pool:
            each_server.join()
        # 告警
        alarm.check_alarm()

        my_log.logger.info('%s 秒后开始下一次轮询' %check_sleep_time)
        time.sleep(check_sleep_time)







