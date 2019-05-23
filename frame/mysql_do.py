#! /usr/bin/python
# encoding:utf-8

import paramiko
import os
import time
import base64
import tools as tools

# 执行命令,
def exec_command(host,user,password,ssh_port,command):
    list = []
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(host, ssh_port, user, password)
        std_in, std_out, std_err = ssh_client.exec_command(command)
        for line in std_out:
            list.append(line.strip("\n"))
        ssh_client.close()
        return list
    except Exception, e:
        print e

# 上传文件
def sftp_upload_file(host,user,password,ssh_port,server_path, local_path):
    try:
        t = paramiko.Transport((host, ssh_port))
        t.connect(username=user, password=password)
        sftp = paramiko.SFTPClient.from_transport(t)
        sftp.put(local_path, server_path)
        t.close()
    except Exception, e:
        print e

#批量上传
def sftp_upload_dir(host,user,password,ssh_port,remote_dir,local_dir):
    try:
        t = paramiko.Transport((host, ssh_port))
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


def mysql_install(host, user, password,ssh_port):
    log_type = 'Mysql部署'
    tools.mysql_exec("delete from many_logs where log_type = 'Mysql部署'", '')

    # 清除目标目录
    cmd = 'rm -rf /tmp/mysql_install'
    exec_command(host, user, password,ssh_port, cmd)
    # 创建文件目录
    cmd = 'mkdir -p /tmp/mysql_install'
    exec_command(host, user, password,ssh_port, cmd)
    # 上传安装部署文件
    sftp_upload_dir(host, user, password, ssh_port,'/tmp', 'mysql_install')
    tools.my_log(log_type, '预上传文件完成！', '')

    # 0. 移除自带MySQL用户及安装包
    cmd = 'sh /tmp/mysql_install/0_mysql_delold.sh > /tmp/mysql_install/0_mysql_delold.log'
    exec_command(host, user, password ,ssh_port, cmd)
    tools.my_log(log_type, '执行0_mysql_delold.sh，移除自带mysql完成！', '')

    # 1. 安装rpm包
    cmd = 'sh /tmp/mysql_install/1_mysql_yum.sh > /tmp/mysql_install/1_mysql_yum.log'
    exec_command(host, user, password, ssh_port, cmd)
    tools.my_log(log_type, '执行1_mysql_yum.sh，rpm包安装完成！', '')

    # 2. 配置资源限制，内核参数
    cmd = 'sh /tmp/mysql_install/2_mysql_init.sh > /tmp/mysql_install/2_mysql_init.log'
    exec_command(host, user, password, ssh_port, cmd)
    tools.my_log(log_type, '执行2_mysql_init.sh，环境初始化完成！', '')

    #3. 配置MySQL用户环境变量
    cmd = 'sh /tmp/mysql_install/3_fd_init.sh > /tmp/mysql_install/3_fd_init.log'
    exec_command(host, user, password, ssh_port, cmd)
    tools.my_log(log_type, '执行3_fd_init.sh.sh，目录创建完成！', '')

    #4. 创建用户组和目录
    cmd = 'sh /tmp/mysql_install/4_mysql_profile.sh > /tmp/mysql_install/4_mysql_profile.log'
    exec_command(host, user, password, ssh_port, cmd)
    tools.my_log(log_type, '执行4_mysql_profile.sh，MySQL用户环境变量配置完成！', '')

# Mysql数据库启停
def mysql_shutdown(host,user,password,ssh_port):
    log_type = '关闭Mysql数据库'
    tools.mysql_exec("delete from many_logs where log_type = '关闭Mysql数据库'", '')
    # 上传脚本
    local_file = os.getcwd() + '/frame/mysql_tools/mysql_shutdown.sh'
    sftp_upload_file(host,user,password, ssh_port, '/tmp/mysql_shutdown.sh',local_file)
    # 执行命令
    cmd = 'sh /tmp/mysql_shutdown.sh > /tmp/mysql_shutdown.log'
    exec_command(host,user,password,ssh_port, cmd)
    tools.my_log(log_type, '执行mysql_shutdown.sh，Mysql数据库关闭成功！', '')


# Mysql数据库启停
def mysql_startup(host,user,password, port):
    log_type = '启动Mysql数据库'
    tools.mysql_exec("delete from many_logs where log_type = '启动Mysql数据库'", '')
    # 上传脚本
    local_file = os.getcwd() + '/frame/mysql_tools/mysql_startup.sh'
    sftp_upload_file(host,user,password,port,'/tmp/mysql_startup.sh',local_file)
    # 执行命令
    cmd = 'sh /tmp/mysql_startup.sh > /tmp/mysql_startup.log'
    exec_command(host,user,password,port, cmd)
    tools.my_log(log_type, 'mysql_startup.sh，Mysql数据库启动成功！', '')

if __name__ == '__main__':
    host = '47.94.97.35'
    user = 'root'
    password = 'Mysql@123'
    mysql_install(host,user,password)


