#! /usr/bin/python
# encoding:utf-8

import paramiko
import os
import time
import base64
import tools as tools

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

def go_start():
    log_type = '程序启停'
    tools.mysql_exec("delete from many_logs where log_type = '程序启停'",'')

    starts = tools.mysql_query(
        "select oper_type,app_name,host,user,password,name,do_cmd,process_check,check_log,id from easy_start_conf order by id")
    for start in starts:
        oper_type = start[0]
        app_name = start[1]
        host = start[2]
        user = start[3]
        password = base64.decodestring(start[4])
        name = start[5]
        do = start[6]
        process_check = start[7]
        check_log = start[8]
        id = start[9]
        # 关闭程序时如执行命令为空，则选择杀进程方式
        if not do and oper_type == 'shutdown':
            cmd_do = 'ps -ef | grep %s| grep -v "grep" | cut -c 9-15 | xargs kill -s 9' % process_check
            exec_log = ''
        # 启动或关闭命令
        if oper_type == 'startup':
            exec_log = '/tmp/%s.log' % name
            cmd_do = "%s > %s 2>&1 &" % (do, exec_log)

        # 检查命令
        cmd_check = 'ps -ef|grep %s |grep -v "grep"' % process_check
        # 异常日志
        if not check_log:
            check_log = exec_log
        error_check = 'tail -100 %s' % check_log
        tools.my_log(log_type,'跳转至%s，对%s执行%s' %(host,name,oper_type),'')
        # 执行关闭或启动命令
        exec_command(host,user,password,cmd_do)

        if oper_type == 'shutdown':
            # 进程数为0，关闭成功
            if len(exec_command(host,user,password,cmd_check)) == 0:
                tools.my_log(log_type, '%s：%s成功！' % (name,oper_type),'')
                upd_sql = "update easy_start_conf set process_check_result='green' where id = %s" %id
                tools.mysql_exec(upd_sql,'')

            else:
                tools.my_log(log_type, '%s：%s失败！' % (name, oper_type),'')
                upd_sql = "update easy_start_conf set process_check_result='red' where id = %s" %id
                tools.mysql_exec(upd_sql,'')
                break

        elif oper_type == 'startup':
            # 进程数为0，启动失败
            if len(exec_command(host,user,password,cmd_check)) == 0:
                # 更新启停状态
                upd_sql = "update easy_start_conf set process_check_result='red' where id = %s" % id
                tools.mysql_exec(upd_sql, '')
                # 异常日志
                err_info = exec_command(host,user,password,error_check)
                err_info_txt = ''
                for i in err_info:
                    err_info_txt = err_info_txt + i
                tools.my_log(log_type, '%s：%s失败！' % (name, oper_type),err_info_txt)
                break
            else:
                upd_sql = "update easy_start_conf set process_check_result='green' where id = %s" % id
                tools.mysql_exec(upd_sql, '')
                err_info = exec_command(host,user,password,error_check)
                err_info_txt = ''
                for i in err_info:
                    err_info_txt = err_info_txt + i
                if 'err' in err_info_txt:
                    upd_sql = "update easy_start_conf set check_log_result='red' where id = %s" % id
                    tools.mysql_exec(upd_sql, '')
                    tools.my_log(log_type, '%s：%s失败！' % (name, oper_type), err_info_txt)
                else:
                    tools.my_log(log_type, '%s：%s成功！' % (name, oper_type),'')
                    upd_sql = "update easy_start_conf set check_log_result='green' where id = %s" % id
                    tools.mysql_exec(upd_sql, '')










