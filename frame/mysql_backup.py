#! /usr/bin/python
# encoding:utf-8
import tools
import os
import datetime


def mysql_fullbackup(host,user,password,user_os,password_os,ssh_port_os,mysql_path,bakdir):
    # 上传脚本
    # 删除旧的备份脚本
    date = datetime.datetime.now().strftime('%Y%m%d%H')
    bak_file = bakdir + '/dbfullbak_%s.sql.gz' %date
    mysqldump = '%s/bin/mysqldump -u%s -p%s -S %s/run/mysql.sock -A -R -x --default-character-set=utf8' %(mysql_path,user,password,mysql_path)

    cmd = mysqldump + ' |gzip > ' + bak_file

    tools.exec_command(host,user_os,password_os,ssh_port_os,cmd)


if __name__ == '__main__':
    host = '192.168.48.50'
    user = 'root'
    password = 'mysqld'
    user_os = 'mysql'
    password_os = 'mysqld'
    mysql_path = '/u01/mysql57'
    bakdir = '/home/mysql/backup'
    mysql_fullbackup(host,user,password,mysql_path,bakdir)
