#! /usr/bin/python
# encoding:utf-8

import MySQLdb
import cx_Oracle
import datetime,time
import ConfigParser
import os
import paramiko
import uuid



host_mysql ='192.168.48.50'
user_mysql = 'root'
password_mysql = 'mysqld'
port_mysql = 3306
dbname = 'db_monitor'


# 上传文件
def sftp_upload_file(host,user,password,server_path, local_path):
    try:
        t = paramiko.Transport((host, 22))
        t.connect(username=user, password=password)
        sftp = paramiko.SFTPClient.from_transport(t)
        sftp.put(local_path, server_path)
        t.close()
    except Exception, e:
        print e

# 操作监控数据存放目标库(mysql)
def mysql_exec(sql,val):
    try:
    	conn=MySQLdb.connect(host=host_mysql,user=user_mysql,passwd=password_mysql,port=int(port_mysql),connect_timeout=5,charset='utf8')
    	conn.select_db(dbname)
    	curs = conn.cursor()
    	if val <> '':
            curs.execute(sql,val)
        else:
            curs.execute(sql)
        conn.commit()
        curs.close()
        conn.close()
    except Exception,e:
       print "mysql execute: " + str(e)


def mysql_query(sql):
    conn=MySQLdb.connect(host=host_mysql,user=user_mysql,passwd=password_mysql,port=int(port_mysql),connect_timeout=5,charset='utf8')
    conn.select_db(dbname)
    cursor = conn.cursor()
    count=cursor.execute(sql)
    if count == 0 :
        result=0
    else:
        result=cursor.fetchall()
    return result
    cursor.close()
    conn.close()

def oracle_query(url,user,password,sql):
    conn = cx_Oracle.connect(user, password, url)
    cursor = conn.cursor()
    count=cursor.execute(sql)
    if count == 0 :
        result=0
    else:
        result=cursor.fetchall()
    return result
    cursor.close()
    conn.close()

def mysql_django_query(sql):
    conn=MySQLdb.connect(host=host_mysql,user=user_mysql,passwd=password_mysql,port=int(port_mysql),connect_timeout=5,charset='utf8')
    conn.select_db(dbname)
    cursor = conn.cursor()
    count = cursor.execute(sql)
    if count == 0:
        result = 0
    else:
        desc = cursor.description
        return [
            dict(zip([col[0] for col in desc], row))
            for row in cursor.fetchall()
            ]
    cursor.close()
    conn.close

def oracle_django_query(user,password,oracle_url,sql):
    conn=cx_Oracle.connect(user,password,oracle_url,encoding = "UTF-8")
    cursor = conn.cursor()
    count = cursor.execute(sql)
    if count == 0:
        result = 0
    else:
        desc = cursor.description
        return [
            dict(zip([col[0] for col in desc], row))
            for row in cursor.fetchall()
            ]
    cursor.close()
    conn.close

def oracle_call_proc(user,password,oracle_url,pro_name):
    conn = cx_Oracle.connect(user, password, oracle_url)
    cursor = conn.cursor()
    cursor.callproc(pro_name)
    cursor.close()
    conn.close()

def now():
    return str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))

def isno(p):
    if p == unicode('启用','utf-8'):
        return 1
    else:
        return 0

def test_orc(host,port,service_name,user,password):
    url = host + ':' + port + '/' + service_name
    try:
        conn = cx_Oracle.connect(user, password, url)
        cur = conn.cursor()
        cur.execute("select 1 from dual")
        result = 1
        result_msg = 'connect success!'
    except Exception,e:
        result = 0
        error_msg = "%s 数据库连接失败：%s" % (url, unicode(str(e), errors='ignore'))

def ora_qry(url,username,password,sql):
    conn = cx_Oracle.connect(username, password, url)
    cur = conn.cursor()
    cur.execute(sql)
    title = [i[0] for i in cur.description]
    g = lambda k: "%-8s" % k
    title = map(g,title)
    result = cur.fetchall()
    return result

def range(range_value):
    if range_value == unicode('1小时', 'utf-8'):
        cpu_range = 1
        begin_time = (datetime.datetime.now() - datetime.timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
    elif range_value== unicode('0.5小时', 'utf-8'):
        cpu_range = 0.5
        begin_time = (datetime.datetime.now() - datetime.timedelta(hours=0.5)).strftime("%Y-%m-%d %H:%M:%S")
    elif range_value == unicode('1天', 'utf-8'):
        cpu_range = 0.5
        begin_time = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    elif range_value == unicode('7天', 'utf-8'):
        cpu_range = 0.5
        begin_time = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
    elif range_value == unicode('30天', 'utf-8'):
        cpu_range = 0.5
        begin_time = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
    return begin_time

def snap_range(range_value):
    if range_value == unicode('1小时', 'utf-8'):
        snap_range = 1
    elif range_value == unicode('1天', 'utf-8'):
        snap_range = 24
    elif range_value == unicode('7天', 'utf-8'):
        snap_range = 7*24
    elif range_value == unicode('30天', 'utf-8'):
        snap_range = 30*24
    return snap_range

def my_log(log_type,log_info,err_info):
    insert_sql = "insert into many_logs(log_type,log_info,err_info) values(%s,%s,%s)"
    value = (log_type, log_info,err_info)
    mysql_exec(insert_sql, value)

def begin_task(task_id,oper_type,server_type,tags,task_name,args):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    insert_sql = "insert into my_task(task_id,server_type,tags,oper_type,task_name,args,start_time,state) values(%s,%s,%s,%s,%s,%s,%s,%s)"
    values = (task_id, server_type, tags, oper_type,task_name, args, now, 'RUNNING')
    mysql_exec(insert_sql,values)

def end_task(task_id,result,state):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    update_sql = "update my_task set result = '%s',end_time = '%s',state = '%s' where task_id = '%s' " %(result,now,state,task_id)
    mysql_exec(update_sql,'')
    update_sql = "update my_task set runtime = abs(timestampdiff(second, end_time, start_time)) where task_id = '%s' " %task_id
    mysql_exec(update_sql,'')


# 执行命令,
def exec_command(host,user,password,command):
    list = []
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(host, 22, user, password)
        std_in, std_out, std_err = ssh_client.exec_command(command)
        for line in std_out:
            list.append(line.strip("\n"))
        ssh_client.close()
        return list
    except Exception, e:
        print e


def task_model(task_model):
    if task_model == unicode('Oracle诊断报告', 'utf-8'):
        task = 'frame.tasks.get_report'
    elif task_model == unicode('Oracle全量备份', 'utf-8'):
        task = 'frame.tasks.oracle_fullbackup'
    elif task_model == unicode('Mysql全量备份', 'utf-8'):
        task = 'frame.tasks.mysql_fullbackup'
    return task


if __name__ == '__main__':
    tags = 'orcl'
    host = '192.168.48.10'
    user = 'dbmon'
    password = 'oracle'
    oper_type = '关闭oracle数据库'
    server_type = 'Oracle'
    task_id = uuid.uuid1()
    task_name = '%s:oracle_shutdow' %tags
    args = 'host：' + host + '，' + 'user：' + user + '，' + 'password：' + password
    begin_task(task_id,oper_type,server_type,tags,task_name,args)
    # oracle.oracle_shutdown(host,user,password)
    result = None
    state = 'SUCCESS'
    end_task(task_id, result, state)
