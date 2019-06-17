#! /usr/bin/python
# encoding:utf-8
import tools
import base64
import cx_Oracle
import os


def oracle_fullbackup(host,user,password,ssh_port,bakdir,sid,backup_retain_day,arch_keep_days):
    # 上传脚本
    # 删除旧的备份脚本
    cmd = 'rm -f %s/oracle_backup_*.sh' %bakdir
    tools.exec_command(host,user,password,ssh_port,cmd)
    # 上传备份脚本
    local_file = os.getcwd() + '/frame/oracle_tools/oracle_backup_db.sh'
    remote_path = '%s/oracle_backup_db.sh' %bakdir
    tools.sftp_upload_file(host, user, password,ssh_port,remote_path, local_file)
    local_file = os.getcwd() + '/frame/oracle_tools/oracle_backup_arch.sh'
    remote_path = '%s/oracle_backup_arch.sh' %bakdir
    tools.sftp_upload_file(host, user, password,ssh_port,remote_path, local_file)
    # 数据库全备
    cmd = "sh %s/oracle_backup_db.sh -i %s -d %s -r %s" % (bakdir, sid, bakdir, backup_retain_day)
    tools.exec_command(host,user,password,ssh_port,cmd)
    # 归档日志清理
    cmd = "sh %s/oracle_backup_arch.sh -i %s -d %s -r %s" % (bakdir, sid, bakdir, arch_keep_days)
    tools.exec_command(host,user,password,ssh_port,cmd)


if __name__ == '__main__':
    host = '192.168.48.10'
    user = 'oracle'
    password = 'oracle'
    bakdir = '/home/oracle/backup'
    oracle_fullbackup(host,user,password,bakdir,'orcl',1,1)
