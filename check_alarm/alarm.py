#! /usr/bin/python
# encoding:utf-8

import ConfigParser
import send_email as mail
import tools as tools
import my_log as my_log
import os

conf = ConfigParser.ConfigParser()

# 间隔固定时间再次发送邮件告警
def is_send_email(alarm_name,tags,url,email_header,alarm_content):
    conf_path = os.path.dirname(os.getcwd())
    conf.read('%s/config/db_monitor.conf' %conf_path)
    receiver = conf.get("email", "receiver").split(',')
    is_send = conf.get("email","is_send")
    next_time_to_send_email = float(conf.get("policy", "next_send_email_time"))
    is_alarm_in_min_sql = "select count(*) from tab_alarm_email_info where tags = '%s' and url='%s' and alarm_type='%s' and email_header = '%s' and timestampdiff(minute,alarm_time,current_timestamp())<%s" % (
        tags,url, alarm_name, email_header,next_time_to_send_email)
    # print is_alarm_in_15min_sql
    is_alarm_in_15min = tools.mysql_query(is_alarm_in_min_sql)
    cnt = is_alarm_in_15min[0][0]
    if cnt == 0 and float(is_send) <> 0:
        try:
            mail.send_email(receiver, email_header, alarm_content)
            my_log.logger.info('成功发送告警邮件: %s 到%s' % (email_header, receiver))
            email_sql = 'insert into tab_alarm_email_info(tags,url,email_header,email_content,alarm_type) value(%s,%s,%s,%s,%s)'
            value = (tags,url, email_header, alarm_content, alarm_name)
            tools.mysql_exec(email_sql, value)
        except Exception, e:
            error_msg = "To %s 发送邮件失败:%s" % (receiver, str(e))
            my_log.logger.error(error_msg)


def alarm():
    my_log.logger.info('初始化告警信息表')
    ins_sql = "insert into tab_alarm_info_his select * from tab_alarm_info"
    tools.mysql_exec(ins_sql,'')
    delete_sql = "delete from tab_alarm_info"
    tools.mysql_exec(delete_sql, '')
    my_log.logger.info('开始巡检主机数据')
    # 主机通断告警
    alarm_name = 'Linux主机通断告警'
    host_stat = tools.mysql_query("select tags,host,host_name,mon_status from os_info")
    if host_stat == 0:
        my_log.logger.warning('未采集到数据：%s' % alarm_name)
    else:
        for line in host_stat:
            tags = str(line[0].encode("utf-8"))
            host_ip = str(line[1].encode("utf-8"))
            host_name = str(line[2].encode("utf-8"))
            host_status = str(line[3].encode("utf-8"))
            url = host_ip + '/' + host_name
            is_alarm = tools.mysql_query("select connect from tab_linux_servers where tags = '%s'" % tags)
            if is_alarm[0][0] == '1':
                if host_status == 'connected error':
                    alarm_content = '%s：Linux主机通断告警 \n 告警时间：%s \n 主机ip：%s \n 主机名：%s \n' % (
                        tags, tools.now(), host_ip, host_name)
                    email_header = '%s：Linux主机通断告警' % tags
                    my_log.logger.info(alarm_content)
                    alarm_sql = 'insert into tab_alarm_info(tags,url,alarm_type,alarm_header,alarm_content) value(%s,%s,%s,%s,%s)'
                    value = (tags, url, alarm_name, email_header, alarm_content,)
                    tools.mysql_exec(alarm_sql, value)
                    is_send_email(alarm_name, tags, url, email_header, alarm_content)
            else:
                my_log.logger.info('%s未设置%s' % (tags, alarm_name))

    # CPU使用率告警
    cpu_conf = tools.mysql_query(
        "select alarm_name,jdg_value from tab_alarm_conf where server_type='Linux' and alarm_name='Linux主机CPU使用率告警'")
    alarm_name = 'Linux主机CPU使用率告警'
    pct_alarm = cpu_conf[0][1]
    cpu_stat = tools.mysql_query("select tags,host,host_name,cpu_used from os_info where cpu_used is not null")
    if cpu_stat == 0:
        my_log.logger.warning('未采集到数据：%s' % alarm_name)
    else:
        for line in cpu_stat:
            tags = str(line[0].encode("utf-8"))
            host_ip = str(line[1].encode("utf-8"))
            host_name = str(line[2].encode("utf-8"))
            cpu_used = float(line[3])
            url = host_ip + '/' + host_name
            is_alarm = tools.mysql_query("select cpu from tab_linux_servers where tags = '%s'" % tags)
            if is_alarm[0][0] == '1':
                if cpu_used > pct_alarm:
                    alarm_content = '%s：Linux主机CPU使用率告警 \n 告警时间：%s \n 主机ip：%s \n 主机名：%s \n CPU使用率：%s%% \n' % (
                        tags, tools.now(), host_ip, host_name, cpu_used)
                    email_header = '%s：Linux主机CPU使用率告警' % tags
                    my_log.logger.info(alarm_content)
                    alarm_sql = 'insert into tab_alarm_info(tags,url,alarm_type,alarm_header,alarm_content) value(%s,%s,%s,%s,%s)'
                    value = (tags, url, alarm_name, email_header, alarm_content,)
                    tools.mysql_exec(alarm_sql, value)
                    is_send_email(alarm_name, tags, url, email_header, alarm_content)
            else:
                my_log.logger.info('%s未设置%s' % (tags, alarm_name))

    # 内存使用率告警
    mem_conf = tools.mysql_query(
        "select alarm_name,jdg_value from tab_alarm_conf where server_type='Linux' and alarm_name='Linux主机内存使用率告警'")
    alarm_name = 'Linux主机内存使用率告警'
    pct_alarm = mem_conf[0][1]
    mem_stat = tools.mysql_query("select tags,host,host_name,mem_used from os_info where mem_used is not null")
    if mem_stat == 0:
        my_log.logger.warning('未采集到数据：%s' % alarm_name)
    else:
        for line in mem_stat:
            tags = str(line[0].encode("utf-8"))
            host_ip = str(line[1].encode("utf-8"))
            host_name = str(line[2].encode("utf-8"))
            mem_used = float(line[3])
            url = host_ip + '/' + host_name
            is_alarm = tools.mysql_query("select mem from tab_linux_servers where tags = '%s'" % tags)
            if is_alarm[0][0] == '1':
                if mem_used > pct_alarm:
                    alarm_content = '%s：Linux主机内存使用率告警 \n 告警时间：%s \n 主机ip：%s \n 主机名：%s \n 内存使用率：%s%% \n' % (
                        tags, tools.now(), host_ip, host_name, mem_used)
                    email_header = '%s：Linux主机内存使用率告警' % tags
                    my_log.logger.info(alarm_content)
                    alarm_sql = 'insert into tab_alarm_info(tags,url,alarm_type,alarm_header,alarm_content) value(%s,%s,%s,%s,%s)'
                    value = (tags, url, alarm_name, email_header, alarm_content,)
                    tools.mysql_exec(alarm_sql, value)
                    is_send_email(alarm_name, tags, url, email_header, alarm_content)
            else:
                my_log.logger.info('%s未设置%s' % (tags, alarm_name))

    # swap使用率告警
    swap_conf = tools.mysql_query(
        "select alarm_name,jdg_value from tab_alarm_conf where server_type='Linux' and alarm_name='Linux主机swap使用率告警'")
    alarm_name = 'Linux主机swap使用率告警'
    pct_alarm = swap_conf[0][1]
    swap_stat = tools.mysql_query("select tags,host,host_name,swap_used,swap_free from os_info where swap_used is not null")
    if mem_stat == 0:
        my_log.logger.warning('未采集到数据：%s' % alarm_name)
    else:
        for line in swap_stat:
            tags = str(line[0].encode("utf-8"))
            host_ip = str(line[1].encode("utf-8"))
            host_name = str(line[2].encode("utf-8"))
            swap_used = float(line[3])
            swap_free = float(line[4])
            swap_used_pct = float(swap_used /(swap_used+swap_free)/2)*100 if swap_used+swap_free<>0 else 0
            url = host_ip + '/' + host_name
            is_alarm = tools.mysql_query("select mem from tab_linux_servers where tags = '%s'" % tags)
            if is_alarm[0][0] == '1':
                if swap_used_pct > pct_alarm:
                    alarm_content = '%s：Linux主机swap使用率告警 \n 告警时间：%s \n 主机ip：%s \n 主机名：%s \n swap使用率：%s%% \n' % (
                        tags, tools.now(), host_ip, host_name, swap_used_pct)
                    email_header = '%s：Linux主机swap使用率告警' % tags
                    my_log.logger.info(alarm_content)
                    alarm_sql = 'insert into tab_alarm_info(tags,url,alarm_type,alarm_header,alarm_content) value(%s,%s,%s,%s,%s)'
                    value = (tags, url, alarm_name, email_header, alarm_content,)
                    tools.mysql_exec(alarm_sql, value)
                    is_send_email(alarm_name, tags, url, email_header, alarm_content)
            else:
                my_log.logger.info('%s未设置%s' % (tags, alarm_name))

    # 文件系统使用率告警
    # 使用率
    disk_conf_pct = tools.mysql_query(
        "select alarm_name,jdg_value,jdg_des from tab_alarm_conf where server_type='Linux' and alarm_name='Linux主机文件系统使用率告警'"
        "and judge='>=' ")
    alarm_name = 'Linux主机文件系统使用率告警'
    pct_alarm = disk_conf_pct[0][1]
    # 剩余空间
    disk_conf_gb = tools.mysql_query(
        "select alarm_name,jdg_value,jdg_des from tab_alarm_conf where server_type='Linux' and alarm_name='Linux主机文件系统使用率告警'"
        "and judge='<=' ")
    gb_alarm = disk_conf_gb[0][1]

    disk_stat = tools.mysql_query(
        "select tags,host,host_name,name,size,avail,pct_used from os_filesystem")
    if disk_stat == 0:
        my_log.logger.warning('未采集到数据：%s' % alarm_name)
    else:
        for line in disk_stat:
            tags = str(line[0].encode("utf-8"))
            host_ip = str(line[1].encode("utf-8"))
            host_name = str(line[2].encode("utf-8"))
            disk_name = str(line[3].encode("utf-8"))
            disk_size = str(line[4].encode("utf-8"))
            disk_avail = str(line[5].encode("utf-8"))
            disk_used = float(line[6])
            url = host_ip + '/' + host_name
            is_alarm = tools.mysql_query("select disk from tab_linux_servers where host = '%s'" % host_ip)
            if is_alarm[0][0] == '1':
                if disk_used > pct_alarm and disk_avail < gb_alarm:
                    alarm_content = '%s：Linux主机文件系统使用率告警 \n 告警时间：%s \n 主机ip：%s \n 主机名：%s \n 目录名称：%s \n 目录总大小：%sGB \n 目录可用：%sGB \n 目录使用率：%s%% \n' % (
                        tags, tools.now(), host_ip, host_name, disk_name, disk_size, disk_avail, disk_used)
                    email_header = '%s：Linux主机文件系统使用率告警' % tags
                    my_log.logger.info(alarm_content)
                    alarm_sql = 'insert into tab_alarm_info(tags,url,alarm_type,alarm_header,alarm_content) value(%s,%s,%s,%s,%s)'
                    value = (tags, url, alarm_name, email_header, alarm_content)
                    tools.mysql_exec(alarm_sql, value)
                    is_send_email(alarm_name, tags, url, email_header, alarm_content)
            else:
                my_log.logger.info('%s未设置%s' % (tags, alarm_name))

    # 数据库通断告警
    my_log.logger.info('开始巡检Oracle数据库数据')
    alarm_name = 'Oracle数据库通断告警'
    db_stat = tools.mysql_query("select tags,host,port,service_name,mon_status from oracle_db")
    if db_stat == 0:
        my_log.logger.warning('未采集到数据：%s' % alarm_name)
    else:
        for line in db_stat:
            tags = str(line[0].encode("utf-8"))
            url = str(line[1].encode("utf-8")) + ':' + str(line[2]) + '/' + str(line[3].encode("utf-8"))
            db_status = str(line[4].encode("utf-8"))
            is_alarm = tools.mysql_query("select connect from tab_oracle_servers where tags = '%s'" % tags)
            if is_alarm[0][0] == '1':
                if db_status == 'connected error':
                    alarm_content = '%s：数据库通断告警 \n 告警时间：%s \n 数据库url：%s \n' % (tags, tools.now(), url)
                    email_header = '%s：数据库通断告警' % tags
                    my_log.logger.info(alarm_content)
                    alarm_sql = 'insert into tab_alarm_info(tags,url,alarm_type,alarm_header,alarm_content) value(%s,%s,%s,%s,%s)'
                    value = (tags, url, alarm_name, email_header, alarm_content,)
                    tools.mysql_exec(alarm_sql, value)
                    is_send_email(alarm_name, tags, url, email_header, alarm_content)
            else:
                my_log.logger.info('%s未设置%s' % (tags, alarm_name))

    # oracle数据库综合性能告警
    my_log.logger.info('开始巡检Oracle数据库等待事件数据')
    event_conf = tools.mysql_query(
        "select alarm_name,jdg_value from tab_alarm_conf where server_type='Oracle' and alarm_name='Oracle数据库综合性能告警'")
    num_max = event_conf[0][1]
    alarm_name = 'Oracle数据库综合性能告警'
    event_sql = ''' select tags, host, port, service_name, cnt_all from (select tags, host, port, service_name, sum(event_cnt) cnt_all
                                from oracle_db_event_his where timestampdiff(minute, chk_time, current_timestamp()) < %s
                                group by tags, host, port, service_name) t where cnt_all > %d ''' %(5,num_max)
    event_stat = tools.mysql_query(event_sql)
    if event_stat == 0:
        my_log.logger.warning('未采集到数据：%s' % alarm_name)
    else:
        for line in event_stat:
            tags = str(line[0].encode("utf-8"))
            url = str(line[1].encode("utf-8")) + ':' + str(line[2]) + '/' + str(line[3].encode("utf-8"))
            event_cnt = str(line[4])
            is_alarm = tools.mysql_query("select oracle_event from tab_oracle_servers where tags = '%s'" % tags)
            if is_alarm[0][0] == '1':
                alarm_content = '%s：数据库综合性能告警 \n 告警时间：%s \n 数据库url：%s \n' % (tags, tools.now(), url)
                email_header = '%s：数据库综合性能告警' % tags
                my_log.logger.info(alarm_content)
                alarm_sql = 'insert into tab_alarm_info(tags,url,alarm_type,alarm_header,alarm_content) value(%s,%s,%s,%s,%s)'
                value = (tags, url, alarm_name, email_header, alarm_content,)
                tools.mysql_exec(alarm_sql, value)
                is_send_email(alarm_name, tags, url, email_header, alarm_content)

            else:
                my_log.logger.info('%s未设置%s' % (tags, alarm_name))

    # 归档使用率告警
    archive_conf = tools.mysql_query(
        "select alarm_name,jdg_value from tab_alarm_conf where server_type='Oracle' and alarm_name='Oracle数据库归档使用率告警'")
    alarm_name = 'Oracle数据库归档使用率告警'
    pct_alarm = archive_conf[0][1]
    archive_stat = tools.mysql_query("select tags,host,port,service_name,archive_used from oracle_db where length(archive_used)>0 ")
    if archive_stat == 0:
        my_log.logger.warning('未采集到数据：%s' % alarm_name)
    else:
        for line in archive_stat:
            tags = str(line[0].encode("utf-8"))
            archive_used = float(line[4])
            url = str(line[1].encode("utf-8")) + ':' + str(line[2]) + '/' + str(line[3].encode("utf-8"))
            is_alarm = tools.mysql_query("select archive from tab_oracle_servers where tags = '%s'" % tags)
            if is_alarm[0][0] == '1':
                if archive_used > pct_alarm:
                    alarm_content = '%s：数据库归档使用率告警 \n 告警时间：%s \n 数据库url：%s \n 使用率：%s%% \n' % (
                        tags, tools.now(), url, archive_used)
                    email_header = '%s：Oracle数据库归档使用率告警' % tags
                    my_log.logger.info(alarm_content)
                    alarm_sql = 'insert into tab_alarm_info(tags,url,alarm_type,alarm_header,alarm_content) value(%s,%s,%s,%s,%s)'
                    value = (tags, url, alarm_name, email_header, alarm_content,)
                    tools.mysql_exec(alarm_sql, value)
                    is_send_email(alarm_name, tags, url, email_header, alarm_content)
            else:
                my_log.logger.info('%s未设置%s' % (tags, alarm_name))


    # 表空间使用率告警
    # 使用率
    tbs_conf_pct = tools.mysql_query(
        "select alarm_name,jdg_value from tab_alarm_conf where server_type='Oracle' and alarm_name='Oracle数据库表空间使用率告警'"
        "and judge='>=' ")
    alarm_name = str(tbs_conf_pct[0][0].encode("utf-8"))
    pct_alarm = tbs_conf_pct[0][1]
    # 剩余空间
    tbs_conf_gb = tools.mysql_query(
        "select alarm_name,jdg_value from tab_alarm_conf where server_type='Oracle' and alarm_name='Oracle数据库表空间使用率告警'"
        "and judge='<=' ")
    gb_alarm = tbs_conf_gb[0][1]

    tbs_stat = tools.mysql_query(
        'select tags,host,port,service_name,tbs_name,size_gb,free_gb,pct_used from oracle_tbs')

    if tbs_stat == 0:
        my_log.logger.warning('未采集到数据：%s' % alarm_name)
    else:
        for line in tbs_stat:
            tags = str(line[0].encode("utf-8"))
            url = str(line[1].encode("utf-8")) + ':' + str(line[2]) + '/' + str(line[3].encode("utf-8"))
            tbs_name = str(line[4].encode("utf-8"))
            tbs_size_gb = float(line[5].encode("utf-8"))
            tbs_pct_used = float(line[7])
            tbs_free_gb = float(line[6].encode("utf-8"))
            is_alarm = tools.mysql_query("select tbs from tab_oracle_servers where tags = '%s'" % tags)
            if is_alarm[0][0] == '1':
                if tbs_pct_used > pct_alarm and tbs_free_gb < gb_alarm:
                    alarm_content = '%s：表空间使用率告警 \n 告警时间：%s \n 数据库url：%s \n 表空间名：%s \n 表空间大小：%sGB \n 表空间使用率：%s%% \n 表空间剩余大小：%sGB \n' % (
                        tags, tools.now(), url, tbs_name, tbs_size_gb, tbs_pct_used, tbs_free_gb)
                    email_header = '%s：%s表空间使用率告警' % (tags, tbs_name)
                    my_log.logger.info(alarm_content)
                    alarm_sql = 'insert into tab_alarm_info(tags,url,alarm_type,alarm_header,alarm_content) value(%s,%s,%s,%s,%s)'
                    value = (tags, url, alarm_name, email_header, alarm_content,)
                    tools.mysql_exec(alarm_sql, value)
                    is_send_email(alarm_name, tags, url, email_header, alarm_content)
            else:
                my_log.logger.info('%s未设置%s' % (tags, alarm_name))

    # adg延迟告警
    adg_conf = tools.mysql_query(
        "select alarm_name,jdg_value from tab_alarm_conf where server_type='Oracle' and alarm_name='Oracle数据库adg延迟告警'")
    alarm_name = 'Oracle数据库adg延迟告警'
    time_alarm = adg_conf[0][1]
    adg_stat = tools.mysql_query(
        "select tags,host,port,service_name,adg_transport_lag,adg_transport_value,adg_apply_lag,adg_apply_value from oracle_db where adg_transport_lag is not null or adg_apply_lag is not null")
    if adg_stat == 0:
        my_log.logger.warning('未采集到数据：%s' % alarm_name)
    else:
        for line in adg_stat:
            tags = str(line[0].encode("utf-8"))
            url = str(line[1].encode("utf-8")) + ':' + str(line[2]) + '/' + str(line[3].encode("utf-8"))
            if line[5] == None:
                my_log.logger.warning('未采集到数据(transport lag)')
                adg_transport_value = '未采集到数据'
            else:
                adg_transport_value = float(line[5])
            if line[7] == None:
                my_log.logger.warning('未采集到数据(apply lag)')
                adg_apply_value = '未采集到数据'
            else:
                adg_apply_value = float(line[7])

            is_alarm = tools.mysql_query("select adg from tab_oracle_servers where tags = '%s'" % tags)
            if is_alarm[0][0] == '1':
                if adg_transport_value > time_alarm or adg_apply_value > time_alarm:
                    alarm_content = '%s：数据库adg延迟告警 \n 告警时间：%s \n 数据库url：%s \n 延迟时间(transport)：%s(秒) \n 延迟时间(apply)：%s(秒) \n' % (
                        tags, tools.now(), url, adg_transport_value, adg_apply_value)
                    email_header = '%s：数据库adg延迟告警' % tags
                    my_log.logger.info(alarm_content)
                    alarm_sql = 'insert into tab_alarm_info(tags,url,alarm_type,alarm_header,alarm_content) value(%s,%s,%s,%s,%s)'
                    value = (tags, url, alarm_name, email_header, alarm_content,)
                    tools.mysql_exec(alarm_sql, value)
                    is_send_email(alarm_name, tags, url, email_header, alarm_content)
            else:
                my_log.logger.info('%s未设置%s' % (tags, alarm_name))
    # 临时表空间使用率告警
    # 使用率
    tmp_tbs_pct_conf = tools.mysql_query(
        "select alarm_name,jdg_value from tab_alarm_conf where server_type='Oracle' and alarm_name='Oracle数据库临时表空间告警'"
        "and judge='>=' ")
    alarm_name = str(tmp_tbs_pct_conf[0][0].encode("utf-8"))
    pct_alarm = tmp_tbs_pct_conf[0][1]
    # 剩余空间
    tmp_tbs_gb_conf = tools.mysql_query(
        "select alarm_name,jdg_value from tab_alarm_conf where server_type='Oracle' and alarm_name='Oracle数据库临时表空间告警'"
        "and judge='<=' ")
    gb_alarm = tmp_tbs_gb_conf[0][1]

    
    tmp_tbs_stat = tools.mysql_query(
        'select tags,host,port,service_name,tmp_tbs_name,total_mb,used_mb,pct_used from oracle_tmp_tbs')

    if tmp_tbs_stat == 0:
        my_log.logger.warning('未采集到数据：%s' % alarm_name)
    else:
        for line in tmp_tbs_stat:
            tags = str(line[0].encode("utf-8"))
            url = str(line[1].encode("utf-8")) + ':' + str(line[2]) + '/' + str(line[3].encode("utf-8"))
            tmp_tbs_name = str(line[4].encode("utf-8"))
            tmp_tbs_total_mb = float(line[5].encode("utf-8"))
            tmp_tbs_used_mb = float(line[6].encode("utf-8"))
            tmp_tbs_pct_used = float(line[7].encode("utf-8"))
            is_alarm = tools.mysql_query("select temp_tbs from tab_oracle_servers where tags = '%s'" % tags)
            if is_alarm[0][0] == '1':
                if tmp_tbs_pct_used > pct_alarm and (tmp_tbs_total_mb - tmp_tbs_used_mb) < gb_alarm:
                    alarm_content = '%s：临时表空间使用率告警 \n 告警时间：%s \n 数据库url：%s \n 临时表空间名：%s \n 临时表空间大小(MB)：%s \n 临时表空间已使用大小(MB)：%s \n 临时表空间使用率：%s%% \n' % (
                        tags, tools.now(), url, tmp_tbs_name, tmp_tbs_total_mb, tmp_tbs_used_mb, tmp_tbs_pct_used)
                    email_header = '%s：%s临时表空间使用率告警' % (tags, tmp_tbs_name)
                    my_log.logger.info(alarm_content)
                    alarm_sql = 'insert into tab_alarm_info(tags,url,alarm_type,alarm_header,alarm_content) value(%s,%s,%s,%s,%s)'
                    value = (tags, url, alarm_name, email_header, alarm_content,)
                    tools.mysql_exec(alarm_sql, value)
                    is_send_email(alarm_name, tags, url, email_header, alarm_content)
            else:
                my_log.logger.info('%s未设置%s' % (tags, alarm_name))

    # undo空间使用率告警
    undo_tbs_pct_conf = tools.mysql_query(
        "select alarm_name,jdg_value from tab_alarm_conf where server_type='Oracle' and alarm_name='Oracle数据库Undo表空间告警'"
        "and judge='>=' ")
    alarm_name = str(undo_tbs_pct_conf[0][0].encode("utf-8"))
    pct_alarm = undo_tbs_pct_conf[0][1]
    # 剩余空间
    undo_tbs_gb_conf = tools.mysql_query(
        "select alarm_name,jdg_value from tab_alarm_conf where server_type='Oracle' and alarm_name='Oracle数据库Undo表空间告警'"
        "and judge='<=' ")
    gb_alarm = undo_tbs_gb_conf[0][1]
    undo_tbs_stat = tools.mysql_query(
        'select tags,host,port,service_name,undo_tbs_name,total_mb,used_mb,pct_used from oracle_undo_tbs')

    if undo_tbs_stat == 0:
        my_log.logger.warning('未采集到数据：%s' % alarm_name)
    else:
        for line in undo_tbs_stat:
            tags = str(line[0].encode("utf-8"))
            url = str(line[1].encode("utf-8")) + ':' + str(line[2]) + '/' + str(line[3].encode("utf-8"))
            undo_tbs_name = str(line[4].encode("utf-8"))
            undo_tbs_total_mb = float(line[5].encode("utf-8"))
            undo_tbs_used_mb = float(line[6].encode("utf-8"))
            undo_tbs_pct_used = float(line[7].encode("utf-8"))
            is_alarm = tools.mysql_query("select undo_tbs from tab_oracle_servers where tags = '%s'" % tags)
            if is_alarm[0][0] == '1':
                if undo_tbs_pct_used > pct_alarm and (undo_tbs_total_mb - undo_tbs_used_mb) < gb_alarm:
                    alarm_content = '%s：undo表空间使用率告警 \n 告警时间：%s \n 数据库url：%s \n undo表空间名：%s \n undo表空间大小(MB)：%s \n undo表空间已使用大小(MB)：%s \n undo表空间使用率：%s%% \n' % (
                        tags, tools.now(), url, undo_tbs_name, undo_tbs_total_mb, undo_tbs_used_mb,
                        undo_tbs_pct_used)
                    email_header = '%s：%sundo表空间使用率告警' % (tags, undo_tbs_name)
                    my_log.logger.info(alarm_content)
                    alarm_sql = 'insert into tab_alarm_info(tags,url,alarm_type,alarm_header,alarm_content) value(%s,%s,%s,%s,%s)'
                    value = (tags, url, alarm_name, email_header, alarm_content,)
                    tools.mysql_exec(alarm_sql, value)
                    is_send_email(alarm_name, tags, url, email_header, alarm_content)
            else:
                my_log.logger.info('%s未设置%s' % (tags, alarm_name))

    # 连接数使用率告警
    conn_conf = tools.mysql_query(
        "select alarm_name,jdg_value from tab_alarm_conf where server_type='Oracle' and alarm_name='Oracle数据库连接数告警'")
    alarm_name = str(conn_conf[0][0].encode("utf-8"))
    pct_alarm = conn_conf[0][1]

    process_stat = tools.mysql_query(
        'select tags,host,port,service_name,max_process,current_process,percent_process from oracle_db where current_process is not null')

    if process_stat == 0:
        my_log.logger.warning('未采集到数据：%s' % alarm_name)
    else:
        for line in process_stat:
            tags = str(line[0].encode("utf-8"))
            url = str(line[1].encode("utf-8")) + ':' + str(line[2]) + '/' + str(line[3].encode("utf-8"))
            if line[4] == None or line[5] == None or line[6] == None:
                my_log.logger.warning('未采集到数据：%s' % alarm_name)
            else:
                max_process = float(line[4])
                current_process = float(line[5])
                process_pct_used = float(line[6])
                is_alarm = tools.mysql_query(
                    "select conn from tab_oracle_servers where tags = '%s'" % tags)
                if is_alarm[0][0] == '1':
                    if process_pct_used > pct_alarm:
                        alarm_content = '%s：连接数告警 \n 告警时间：%s \n 数据库url：%s \n 最大连接数：%s \n 已使用连接数：%s \n 连接数使用率百分比：%s%% \n' % (
                            tags, tools.now(), url, max_process, current_process, process_pct_used)
                        email_header = '%s：连接数告警' % tags
                        my_log.logger.info(alarm_content)
                        alarm_sql = 'insert into tab_alarm_info(tags,url,alarm_type,alarm_header,alarm_content) value(%s,%s,%s,%s,%s)'
                        value = (tags, url, alarm_name, email_header, alarm_content,)
                        tools.mysql_exec(alarm_sql, value)
                        is_send_email(alarm_name, tags, url, email_header, alarm_content)
                else:
                    my_log.logger.info('%s未设置%s' % (tags, alarm_name))

    # 无效索引告警
    alarm_name = 'Oracle失效索引告警'
    index_stat = tools.mysql_query("select tags,host,port,service_name,owner,index_name,partition_name,status from oracle_invalid_index")
    if index_stat == 0:
        my_log.logger.warning('未采集到数据：%s' % alarm_name)
    else:
        for line in index_stat:
            tags = str(line[0].encode("utf-8"))
            url = str(line[1].encode("utf-8")) + ':' + str(line[2]) + '/' + str(line[3].encode("utf-8"))
            is_alarm = tools.mysql_query("select invalid_index from tab_oracle_servers where tags = '%s'" % tags)
            if is_alarm[0][0] == '1':
                owner = str(line[4])
                index_name = str(line[5])
                partition_name = str(line[6])
                status = str(line[7])
                alarm_content = '%s：数据库失效索引 \n 告警时间：%s \n 数据库url：%s \n 用户：%s \n 索引名称：%s \n 分区名称：%s \n 索引状态：%s \n' % (
                    tags, tools.now(), url, owner,index_name,partition_name,status)
                email_header = '%s：数据库失效索引告警' % tags
                my_log.logger.info(alarm_content)
                alarm_sql = 'insert into tab_alarm_info(tags,url,alarm_type,alarm_header,alarm_content) value(%s,%s,%s,%s,%s)'
                value = (tags, url, alarm_name, email_header, alarm_content,)
                tools.mysql_exec(alarm_sql, value)
                is_send_email(alarm_name, tags, url, email_header, alarm_content)
            else:
                my_log.logger.info('%s未设置%s' % (tags, alarm_name))

    # 锁异常告警
    alarm_name = 'Oracle锁异常告警'
    oracle_lock_conf = tools.mysql_query(
        "select alarm_name,jdg_value from tab_alarm_conf where server_type='Oracle' and alarm_name='Oracle数据库锁异常告警'")
    time_max = oracle_lock_conf[0][1]
    lock_sql = "select tags,host,port,service_name,session,ctime,inst_id,type from oracle_lock where session like 'Waiter%%' and ctime > '%s'" %time_max
    lock_stat = tools.mysql_query(lock_sql)
    if lock_stat == 0:
        my_log.logger.warning('未采集到数据：%s' % alarm_name)
    else:
        for line in lock_stat:
            tags = str(line[0].encode("utf-8"))
            url = str(line[1].encode("utf-8")) + ':' + str(line[2]) + '/' + str(line[3].encode("utf-8"))
            is_alarm = tools.mysql_query(
                "select oracle_lock from tab_oracle_servers where tags = '%s'" % tags)
            if is_alarm[0][0] == '1':
                session = str(line[4])
                ctime = str(line[5])
                inst_id = str(line[6])
                type = str(line[7])
                alarm_content = '%s：数据库锁异常 \n 告警时间：%s \n 数据库url：%s \n 会话SID：%s \n 等待时间：%s(秒) \n 实例编号：%s \n 锁类型：%s \n' % (
                    tags, tools.now(), url, session, ctime, inst_id, type)
                email_header = '%s：数据库锁异常告警' % tags
                my_log.logger.info(alarm_content)
                alarm_sql = 'insert into tab_alarm_info(tags,url,alarm_type,alarm_header,alarm_content) value(%s,%s,%s,%s,%s)'
                value = (tags, url, alarm_name, email_header, alarm_content,)
                tools.mysql_exec(alarm_sql, value)
                is_send_email(alarm_name, tags, url, email_header, alarm_content)
            else:
                my_log.logger.info('%s未设置%s' % (tags, alarm_name))

    # 密码过期告警
    alarm_name = '密码过期告警'
    pwd_stat = tools.mysql_query(
        "select tags,host,port,service_name,username,result_number from oracle_expired_pwd")
    if pwd_stat == 0:
        my_log.logger.warning('未采集到数据：%s' % alarm_name)
    else:
        for line in pwd_stat:
            tags = str(line[0].encode("utf-8"))
            url = str(line[1].encode("utf-8")) + ':' + str(line[2]) + '/' + str(line[3].encode("utf-8"))
            is_alarm = tools.mysql_query(
                "select oracle_pwd from tab_oracle_servers where tags = '%s'" % tags)
            if is_alarm[0][0] == '1':
                username = str(line[4])
                result_number = str(line[5])
                alarm_content = '%s：数据库用户密码过期 \n 告警时间：%s \n 数据库url：%s \n 用户名：%s \n 到期时间：%s \n' % (
                    tags, tools.now(), url, username, result_number)
                email_header = '%s：数据库用户密码过期告警' % tags
                my_log.logger.info(alarm_content)
                alarm_sql = 'insert into tab_alarm_info(tags,url,alarm_type,alarm_header,alarm_content) value(%s,%s,%s,%s,%s)'
                value = (tags, url, alarm_name, email_header, alarm_content,)
                tools.mysql_exec(alarm_sql, value)
                is_send_email(alarm_name, tags, url, email_header, alarm_content)
            else:
                my_log.logger.info('%s未设置%s' % (tags, alarm_name))


    # 数据库后台日志告警
    alarm_name = 'Oracle后台日志告警'
    db_stat = tools.mysql_query("select tags,host,port,service_name,err_info from oracle_db")
    if db_stat == 0:
        my_log.logger.warning('未采集到数据：%s' % alarm_name)
    else:
        for line in db_stat:
            tags = str(line[0].encode("utf-8"))
            url = str(line[1].encode("utf-8")) + ':' + str(line[2]) + '/' + str(line[3].encode("utf-8"))
            is_alarm = tools.mysql_query("select err_info from tab_oracle_servers where tags = '%s'" % tags)
            if is_alarm[0][0] == '1':
                if str(line[4]) != 'None' and str(line[4]):
                    err_info = str(line[4])
                    alarm_content = '%s：数据库后台日志 \n 告警时间：%s \n 数据库url：%s \n 异常信息：%s \n' % (
                        tags, tools.now(), url, err_info)
                    email_header = '%s：数据库后台日志告警' % tags
                    my_log.logger.info(alarm_content)
                    alarm_sql = 'insert into tab_alarm_info(tags,url,alarm_type,alarm_header,alarm_content) value(%s,%s,%s,%s,%s)'
                    value = (tags, url, alarm_name, email_header, alarm_content,)
                    tools.mysql_exec(alarm_sql, value)
                    is_send_email(alarm_name, tags, url, email_header, alarm_content)
            else:
                my_log.logger.info('%s未设置%s' % (tags, alarm_name))

    # mysql数据库通断告警
    my_log.logger.info('开始巡检Mysql数据库数据')
    alarm_name = 'MySQL数据库通断告警'
    db_stat = tools.mysql_query("select tags,host,port,mon_status from mysql_db")
    if db_stat == 0:
        my_log.logger.warning('未采集到数据：%s' % alarm_name)
    else:
        for line in db_stat:
            tags = str(line[0].encode("utf-8"))
            url = str(line[1].encode("utf-8")) + ':' + str(line[2])
            db_status = str(line[3].encode("utf-8"))
            is_alarm = tools.mysql_query("select connect from tab_mysql_servers where tags = '%s'" % tags)
            if is_alarm[0][0] == '1':
                if db_status == 'connected error':
                    alarm_content = '%s：MySQL数据库通断告警 \n 告警时间：%s \n 数据库url：%s \n' % (tags, tools.now(), url)
                    email_header = '%s：MySQL数据库通断告警' % tags
                    my_log.logger.info(alarm_content)
                    alarm_sql = 'insert into tab_alarm_info(tags,url,alarm_type,alarm_header,alarm_content) value(%s,%s,%s,%s,%s)'
                    value = (tags, url, alarm_name, email_header, alarm_content,)
                    tools.mysql_exec(alarm_sql, value)
                    is_send_email(alarm_name, tags, url, email_header, alarm_content)
            else:
                my_log.logger.info('%s未设置%s' % (tags, alarm_name))



if __name__ == '__main__':
    alarm()