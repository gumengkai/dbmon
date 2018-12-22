#! /usr/bin/python
# encoding:utf-8

import os
import MySQLdb
import time
import ConfigParser
import hashlib
import base64

conf = ConfigParser.ConfigParser()
conf_path = os.path.dirname(os.getcwd())
conf.read('%s/config/db_monitor.conf' %conf_path)
host_mysql =conf.get("target_mysql","host")
user_mysql = conf.get("target_mysql","user")
password_mysql = conf.get("target_mysql","password")
port_mysql = conf.get("target_mysql","port")
dbname = conf.get("target_mysql","dbname")

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



def now():
    return str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))

def get_rate_level(rate):
    if rate >= 90:
        rate_level = 'red'
    elif rate >= 80 and rate < 90:
        rate_level = 'yellow'
    else:
        rate_level = 'green'
    return rate_level

def get_decute(value):
    if value < 60:
        decute = 0
    # 使用率在60至80，扣分不超过20
    elif value >= 60 and value < 80:
        decute = value - 60
    # 使用率在80以上，扣分在40以上但不超过50，不及格
    elif value >= 80 and value < 90:
        decute = 40 + (value - 80)
    # 使用率超过90%，扣分在90分以上
    else:
        decute = 90 + (value - 90)
    return decute

def get_decute_tbs(tbs_used,tbs_free):
    # 使用率在80%以下或剩余空间大于10G，不扣分
    if tbs_used < 80 or tbs_free > 0.001:
        decute = 0
    # 使用率大于80%、小于90%且剩余空间小于10G，剩余空间越小，扣分越多(至多扣100)，使用率越高，扣分越多(至多扣20分)，取两者的较大值
    elif tbs_used >= 80 and tbs_used < 90 and tbs_free <= 10:
        decute = max((10-tbs_free) * 10,(tbs_used-80)*4)
    # 使用率在80以上，扣分在40以上但不超过50，不及格
    elif tbs_used >= 90 and tbs_free <= 10 :
        decute = max((10 - tbs_free) * 10, (tbs_used - 90)*10 )
    # 使用率超过90%，扣分在90分以上
    return decute

def get_decute_undo_tbs(undo_tbs_used,undo_tbs_free):
    # 使用率在80%以下或剩余空间大于5G，不扣分
    if undo_tbs_used < 80 or undo_tbs_free > 5:
        decute = 0
    # 使用率大于80%、小于90%且剩余空间小于10G，剩余空间越小，扣分越多(至多扣100)，使用率越高，扣分越多(至多扣20分)，取两者的较大值
    elif undo_tbs_used >= 80 and undo_tbs_used < 90 and undo_tbs_free <= 10:
        decute = max((10-undo_tbs_free) * 10,(undo_tbs_used-80)*4)
    # 使用率在80以上，扣分在40以上但不超过50，不及格
    elif undo_tbs_used >= 90 and undo_tbs_free <= 10 :
        decute = max((10 - undo_tbs_free) * 10, (undo_tbs_used - 90)*10 )
    # 使用率超过90%，扣分在90分以上
    return decute

def get_decute_tmp_tbs(tmp_tbs_used,tmp_tbs_free):
    # 使用率在80%以下或剩余空间大于5G，不扣分
    if tmp_tbs_used < 80 or tmp_tbs_free > 5:
        decute = 0
    # 使用率大于80%、小于90%且剩余空间小于10G，剩余空间越小，扣分越多(至多扣100)，使用率越高，扣分越多(至多扣20分)，取两者的较大值
    elif tmp_tbs_used >= 80 and tmp_tbs_used < 90 and tmp_tbs_free <= 10:
        decute = max((10-tmp_tbs_free) * 10,(tmp_tbs_used-80)*4)
    # 使用率在80以上，扣分在40以上但不超过50，不及格
    elif tmp_tbs_used >= 90 and tmp_tbs_free <= 10 :
        decute = max((10 - tmp_tbs_free) * 10, (tmp_tbs_used - 90)*10 )
    # 使用率超过90%，扣分在90分以上
    return decute


def md5(str,what):
    m5 = hashlib.md5()
    m5.update(str)
    md5_str = m5.hexdigest()
    return md5_str



if __name__ == '__main__':
    print base64.encodestring('oracle')
    print base64.decodestring('b3JhY2xl')
    print os.path.dirname(os.getcwd())


