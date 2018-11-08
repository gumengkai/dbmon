#! /usr/bin/python
# encoding:utf-8

import paramiko
import time
import os
import re
import codecs
import commands
from time import  localtime
from datetime import datetime,date
import base64
import tools as tools



# 执行命令
def sftp_exec_command(host,user,password,command):
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

# 下载文件
def sftp_down_file(host,user,password,server_path, local_path):
    try:
        t = paramiko.Transport((host, 22))
        t.connect(username=user, password=password)
        sftp = paramiko.SFTPClient.from_transport(t)
        sftp.get(server_path, local_path)
        t.close()
    except Exception, e:
        print e

# 读配置文件
def read_conf(loc_conf):
    l = []
    conf = open(loc_conf, 'r');
    for line in conf:
        dic = dict()
        if  line.startswith('host'):
            lst = line.strip().split(',')
            for i in xrange(len(lst)):
                str = lst[i]
                idx = str.index('=')
                key = str[0:idx]
                value = str[idx + 1:]
                dic[key] = value
            l.append(dic)
    return l
# 加密
def encry(cnf_org):
    f_org = open(cnf_org,'r')
    content = f_org.read()
    content1 = content.encode(encoding='utf-8')
    content2 = base64.b64encode(content1)
    f_org.close()
    with open(cnf_org,'wb+') as f_org:
        f_org.write(content2)
# 解密
def deci(cnf_now):
    f_now = open(cnf_now,'r')
    content = f_now.read()
    content1 = base64.b64decode((content))
    with open(cnf_now,'wb+') as f_now:
        f_now.write(content1)

def go_collect(local_dir):
    log_type = '日志采集'
    tools.mysql_exec("delete from many_logs where log_type = '日志采集'",'')
    # 指定本地保存路径
    today = time.strftime('%Y%m%d')
    now = time.strftime('%H%M%S')
    # 创建当天目录
    local_today = local_dir +'/' + today
    isExists = os.path.exists(local_today)
    # cmd_find = "find %s -mtime 0 -name '*'" %log_path
    if not isExists:
        os.mkdir(local_today)
    tools.my_log(log_type,'成功创建本地目录：%s' % local_today,'')

    logs = tools.mysql_query(
        "select app_name, host,user,password,log_name,log_path from log_collect_conf order by id")
    print logs
    for log in logs:
        app_name = log[0]
        host = log[1]
        user = log[2]
        password = base64.decodestring(log[3])
        log_name = log[4]
        log_path = log[5]
        # 创建程序目录
        local_log_path = local_today + '/' + log_name
        isExists = os.path.exists(local_log_path)
        # cmd_find = "find %s -mtime 0 -name '*.trc'" %log_path
        if not isExists:
            os.makedirs(local_log_path)
        tools.my_log(log_type, '成功创建本地日志目录：%s' % local_log_path,'')

        # 将远端日志路径传入app_path_list，进行遍历抓取
        log_list = []
        log_list.append(log_path)
        for log_path in log_list:
            tools.my_log(log_type, '开始收集日志：%s->%s->%s' % (log_name,host,log_path),'')
            cmd_find = "find %s -newermt %s -type f -name '*' ! -name '.*'" % (log_path, today)
            lt = sftp_exec_command(host,user,password,cmd_find)
            for each in lt:
                # 取文件名
                filename = each.split('/')[-1]
                local_app_log = local_log_path + '/' + filename
                print each
                print local_app_log
                sftp_down_file(host,user,password,each, local_app_log)
                # alert_path_final=alert_path.decode('unicode-escape').encode('utf-8')
                tools.my_log(log_type,'成功获取日志：%s' %each,'')


