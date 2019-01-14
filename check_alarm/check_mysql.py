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
    curs.execute("show global status")
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

# big_table
def get_mysql_big_table(conn):
    cur = conn.cursor()
    sql = "SELECT table_schema as 'DB',table_name as 'TABLE',CONCAT(ROUND(( data_length + index_length ) / ( 1024 * 1024 ), 2), '') 'TOTAL' , table_comment as COMMENT FROM information_schema.TABLES ORDER BY data_length + index_length DESC ;"
    cur.execute(sql)
    return cur.fetchall()
