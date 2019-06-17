#! /usr/bin/python
# encoding:utf-8

# Create your tasks here

from __future__ import absolute_import,unicode_literals
from celery import shared_task
import frame.oracle_do as oracle
import frame.oracle_backup as oracle_bak

import frame.mysql_do as mysql
import frame.mysql_backup as mysql_bak
import frame.mysql_install as mysql_ins

import uuid
import frame.tools as tools

# mysql安装
@shared_task
def mysql_install(host,user,password,ssh_port,data_path,mysql_base,port):
    oper_type = '安装MySQL数据库'
    server_type = 'MySQL'
    task_id = uuid.uuid1()
    task_name = '%s:mysql_install' % host
    args = 'host：' + host + '，' + 'user：' + user + '，' + 'password：' + password + \
           'data_path: ' + data_path + 'mysql_base: ' +mysql_base + 'port: ' + port
    tools.begin_task(task_id, oper_type, server_type, host, task_name, args)
    mysql_ins.mysql_install(host, user, password,ssh_port,data_path,mysql_base,port)
    result = ''
    state = 'SUCCESS'
    tools.end_task(task_id, result, state)

# mysql全量备份
@shared_task
def mysql_fullbackup(tags,host,user,password,user_os,password_os,ssh_port_os,mysql_path,bakdir):
    oper_type = 'Mysql全量备份'
    server_type = 'Mysql'
    task_id = uuid.uuid1()
    task_name = '%s:mysql_fullbak' %tags
    args = 'tags：' + tags + '，'  + 'host：' + host  + 'user：' + user_os\
         + '，' +  'password：' + password_os + '，' + 'ssh_port_os：' + str(ssh_port_os) + '，' + 'mysql_path：' + mysql_path + '，' + 'bakdir：' + bakdir
    tools.begin_task(task_id,oper_type,server_type,tags,task_name,args)
    mysql_bak.mysql_fullbackup(host,user,password,user_os,password_os,ssh_port_os,mysql_path,bakdir)
    result = ''
    state = 'SUCCESS'
    tools.end_task(task_id,result,state)
