#! /usr/bin/python
# encoding:utf-8

import cx_Oracle
import MySQLdb
import time
import os
import paramiko
import re
# os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'

# 取指定参数
def get_mysql_para(conn,par):
    curs = conn.cursor()
    para = curs.execute("show global variables like '%s'" %par)
    para_list = curs.fetchall()
    curs.close()
    return para_list[0][1]

# 取状态
def get_mysql_status(conn):
    curs = conn.cursor()
    mysql_stat = curs.execute("show global status")
    mysql_stat_list = curs.fetchall()
    mysql_stat_dict = {}
    for item in mysql_stat_list:
        mysql_stat_dict[item[0]] = item[1]
    curs.close()
    return mysql_stat_dict

# 获取等待线程
def get_mysql_waits(conn):
    try:
        conn.select_db('information_schema')
        curs=conn.cursor()
        curs.execute("select count(1) from processlist where state <> '' and user <> 'repl' and time > 2");
        result = curs.fetchone()[0]
        return result

    except Exception,e:

        print e
    finally:
        curs.close()
