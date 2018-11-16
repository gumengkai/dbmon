#! /usr/bin/python
# encoding:utf-8

import paramiko
import os
import time
import base64
import tools as tools

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

#批量上传
def sftp_upload_dir(host,user,password,remote_dir,local_dir):
    try:
        t = paramiko.Transport((host, 22))
        t.connect(username=user, password=password)
        sftp = paramiko.SFTPClient.from_transport(t)
        for root,dirs,files in os.walk(local_dir):
            print root,dirs,files
            # remote_path = remote_dir + '/' + dirs
            for filespatch in files:
                local_file = os.path.join(root,filespatch)
                a = local_file.replace(local_dir,'')
                remote_file = remote_dir +'/' + local_file.replace("\\", "/")
                sftp.put(local_file, remote_file)
                print '成功上传：%s 到 %s' %(local_file,remote_file)

    except Exception,e:
        print e

def mysql_install(host,user,password):
    log_type = 'Mysql部署'
    tools.mysql_exec("delete from many_logs where log_type = 'Mysql部署'", '')

    #3. 配置MySQL用户环境变量
    cmd = 'sh /tmp/mysql_install/3_mysql_profile.sh > /tmp/mysql_install/3_mysql_profile.log'
    exec_command(host, user, password, cmd)
    tools.my_log(log_type, '执行3_mysql_profile.sh，MySQL用户环境变量配置完成！', '')

    #4. 创建用户组和目录
    cmd = 'sh /tmp/mysql_install/4_fd_init.sh > /tmp/mysql_install/4_fd_init.log'
    exec_command(host, user, password, cmd)
    tools.my_log(log_type, '执行4_fd_init.sh，目录创建完成！', '')

    #5.解压、安装
    cmd = 'sh /tmp/mysql_install/5_mysql_install.sh > /tmp/mysql_install/5_mysql_install.log'
    exec_command(host, user, password, cmd)
    tools.my_log(log_type, '执行5_mysql_install.sh，mysql安装完成！', '')

# Mysql数据库启停
def mysql_shutdown(host,user,password):
    log_type = '关闭Mysql数据库'
    tools.mysql_exec("delete from many_logs where log_type = '关闭Mysql数据库'", '')
    # 上传脚本
    local_file = os.getcwd() + '/frame/mysql_tools/mysql_shutdown.sh'
    sftp_upload_file(host,user,password,'/tmp/mysql_shutdown.sh',local_file)
    # 执行命令
    cmd = 'sh /tmp/mysql_shutdown.sh > /tmp/mysql_shutdown.log'
    exec_command(host,user,password,cmd)
    tools.my_log(log_type, '执行mysql_shutdown.sh，Mysql数据库关闭成功！', '')


# Mysql数据库启停
def mysql_startup(host,user,password):
    log_type = '启动Mysql数据库'
    tools.mysql_exec("delete from many_logs where log_type = '启动Mysql数据库'", '')
    # 上传脚本
    local_file = os.getcwd() + '/frame/mysql_tools/mysql_startup.sh'
    sftp_upload_file(host,user,password,'/tmp/mysql_startup.sh',local_file)
    # 执行命令
    cmd = 'sh /tmp/mysql_startup.sh > /tmp/mysql_startup.log'
    exec_command(host,user,password,cmd)
    tools.my_log(log_type, 'mysql_startup.sh，Mysql数据库启动成功！', '')

if __name__ == '__main__':
    host = '114.115.244.52'
    user = 'root'
    password = 'Mysql_123'
    mysql_install(host,user,password)


