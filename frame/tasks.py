#! /usr/bin/python
# encoding:utf-8

# Create your tasks here

from __future__ import absolute_import,unicode_literals
from celery import shared_task
import frame.oracle_do as oracle
import frame.oracle_backup as oracle_bak

import frame.mysql_do as mysql
import frame.mysql_backup as mysql_bak

import uuid
import frame.tools as tools

@shared_task
def add(x,y):
    return x+y

#关闭数据库
@shared_task
def oracle_shutdown(tags,host,user,password):
    oper_type = '关闭oracle数据库'
    server_type = 'Oracle'
    task_id = uuid.uuid1()
    task_name = '%s:oracle_shutdow' %tags
    args = 'host：' + host + '，' + 'user：' + user + '，' + 'password：' + password
    tools.begin_task(task_id,oper_type,server_type,tags,task_name,args)
    oracle.oracle_shutdown(host,user,password)
    result = ''
    state = 'SUCCESS'
    tools.end_task(task_id,result,state)

#启动数据库
@shared_task
def oracle_startup(tags,host,user,password):
    oper_type = '启动oracle数据库'
    server_type = 'Oracle'
    task_id = uuid.uuid1()
    task_name = '%s:oracle_startup' %tags
    args = 'host：' + host + '，' + 'user：' + user + '，' + 'password：' + password
    tools.begin_task(task_id,oper_type,server_type,tags,task_name,args)
    oracle.oracle_startup(host,user,password)
    result = ''
    state = 'SUCCESS'
    tools.end_task(task_id,result,state)

#重启数据库
@shared_task
def oracle_restart(tags,host,user,password):
    oper_type = '重启oracle数据库'
    server_type = 'Oracle'
    task_id = uuid.uuid1()
    task_name = '%s:oracle_restart' %tags
    args = 'host：' + host + '，' + 'user：' + user + '，' + 'password：' + password
    tools.begin_task(task_id,oper_type,server_type,tags,task_name,args)
    oracle.oracle_shutdown(host,user,password)
    oracle.oracle_startup(host, user, password)
    result = ''
    state = 'SUCCESS'
    tools.end_task(task_id,result,state)

# 安装数据库
@shared_task
def oracle_install(host,user,password):
    oracle.oracle_install(host,user,password)

# 执行Oracle数据库脚本
@shared_task
def oracle_exec_sql():
    oracle.oracle_exec_sql()

# oracle容灾切换
@shared_task
def oracle_switchover(primary_tags,p_host,p_user,p_password,standby_tags,s_host,s_user,s_password):
    oper_type = 'Oracle容灾切换'
    server_type = 'Oracle'
    task_id = uuid.uuid1()
    task_name = '%s<-->%s:oracle_switchover' %(primary_tags,standby_tags)
    args = 'p_host：' + p_host + '，' + 'p_user：' + p_user + '，' + 'p_password：' + p_password \
         + '，' +  's_host：' + s_host + '，' + 's_user：' + s_user + '，' + 's_password：' + s_password
    tools.begin_task(task_id,oper_type,server_type,primary_tags + '，' +standby_tags,task_name,args)
    oracle.oracle_switchover(p_host,p_user,p_password,s_host,s_user,s_password)
    result = ''
    state = 'SUCCESS'
    tools.end_task(task_id,result,state)

# 获取oracle性能报告
@shared_task
def get_report(tags,host,user,password,user_os,password_os,service_name,url,report_type,begin_snap,end_snap):
    oper_type = 'Oracle性能报告'
    server_type = 'Oracle'
    task_id = uuid.uuid1()
    task_name = '%s:oracle_rpt' %tags
    args = 'tags：' + tags + '，' + 'url：' + url + '，' + 'user：' + user \
         + '，' +  'password：' + password + '，' + 'report_type：' + report_type + '，' + 'begin_snap：' + begin_snap +'，' + 'end_snap：' + end_snap
    tools.begin_task(task_id,oper_type,server_type,tags,task_name,args)
    oracle.get_report(tags,url,user,password,report_type,begin_snap,end_snap)
    result = ''
    state = 'SUCCESS'
    tools.end_task(task_id,result,state)

# oracle全量备份
@shared_task
def oracle_fullbackup(tags,host,user,password,user_os,password_os,service_name,url,bakdir,backup_retain_day,arch_keep_days):
    oper_type = 'Oracle全量备份'
    server_type = 'Oracle'
    task_id = uuid.uuid1()
    task_name = '%s:oracle_fullbak' %tags
    args = 'tags：' + tags + '，'  + 'host：' + host  + 'user：' + user_os\
         + '，' +  'password：' + password_os + '，' + 'bakdir：' + bakdir + '，' + 'sid：' + service_name +'，' + 'backup_retain_day：' + backup_retain_day + 'arch_keep_days：' + arch_keep_days
    tools.begin_task(task_id,oper_type,server_type,tags,task_name,args)
    oracle_bak.oracle_fullbackup(host,user_os,password_os,bakdir,service_name,backup_retain_day,arch_keep_days)
    result = ''
    state = 'SUCCESS'
    tools.end_task(task_id,result,state)



# oracle日志挖掘
@shared_task
def oracle_logmnr(tags,url,user,password,schema,object,operation,log_list):
    oper_type = 'oracle日志挖掘'
    server_type = 'Oracle'
    task_id = uuid.uuid1()
    task_name = '%s:oracle_logmnr' %tags
    args = 'tags：%s url：%s user：%s password：%s schema：%s bject：%s operation：%s' %(tags,url,user,password,schema,object,operation)
    tools.begin_task(task_id,oper_type,server_type,tags,task_name,args)
    oracle.oracle_logmnr(url,user,password,schema,object,operation,log_list)
    result = ''
    state = 'SUCCESS'
    tools.end_task(task_id,result,state)

# mysql安装
@shared_task
def mysql_install(host,user,password):
    oper_type = '安装mysql数据库'
    server_type = 'Mysql'
    task_id = uuid.uuid1()
    task_name = '%s:mysql_install' % host
    args = 'host：' + host + '，' + 'user：' + user + '，' + 'password：' + password
    tools.begin_task(task_id, oper_type, server_type, host, task_name, args)
    mysql.mysql_install(host, user, password)
    result = ''
    state = 'SUCCESS'
    tools.end_task(task_id, result, state)

# mysql全量备份
@shared_task
def mysql_fullbackup(tags,host,user,password,user_os,password_os,mysql_path,bakdir):
    oper_type = 'Mysql全量备份'
    server_type = 'Mysql'
    task_id = uuid.uuid1()
    task_name = '%s:mysql_fullbak' %tags
    args = 'tags：' + tags + '，'  + 'host：' + host  + 'user：' + user_os\
         + '，' +  'password：' + password_os + '，' + 'mysql_path：' + mysql_path + '，' + 'bakdir：' + bakdir
    tools.begin_task(task_id,oper_type,server_type,tags,task_name,args)
    mysql_bak.mysql_fullbackup(host,user,password,user_os,password_os,mysql_path,bakdir)
    result = ''
    state = 'SUCCESS'
    tools.end_task(task_id,result,state)