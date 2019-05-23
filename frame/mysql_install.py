#! /ur/bin/python
# encoding: utf-8

import paramiko
import ConfigParser
import os
import tools

log_type = 'MySQL部署'

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
def sftp_upload_file(host,user,password,ssh_port,local_path, remote_path):
    try:
        t = paramiko.Transport((host, ssh_port))
        t.connect(username=user, password=password)
        sftp = paramiko.SFTPClient.from_transport(t)
        sftp.put(local_path, remote_path)
        t.close()
    except Exception, e:
        print e

# mysql目录
def get_dir_for_mysql(mysql_base, port):
    mysql_home = '%s/my%s' % (mysql_base, port)
    mysql_run = '%s/run' % mysql_home
    mysql_tmp = '%s/tmp' % mysql_home
    mysql_log = '%s/log' % mysql_home
    mysql_binlog = '%s/log/binlog' % mysql_home
    mysql_iblog = '%s/log/iblog' % mysql_home

    return (mysql_home, mysql_run,mysql_tmp, mysql_log, mysql_binlog,mysql_iblog)


def create_home_dir(host,user,password,ssh_port,port,data_path,mysql_base):
    # 创建MySQL目录
    dirs = get_dir_for_mysql(mysql_base,port)
    for dir in dirs:
        cmd = 'mkdir -p %s' %dir
        exec_command(host,user,password,cmd)
        tools.my_log(log_type, '创建目录%s！'%dir, '')
    # 创建数据目录
    datadir = '%s/my%s' %(data_path,port)
    cmd = 'mkdir -p %s' %datadir
    exec_command(host, user, password,ssh_port, cmd)
    tools.my_log(log_type, '创建目录%s！' % datadir, '')
    tools.my_log(log_type, '创建目录完成！', '')


def read_cnf_template():
    conf_template_dir = os.getcwd()
    filename = conf_template_dir + '/frame/mysql_install/my.cnf_template'
    print filename
    parser = ConfigParser.ConfigParser(allow_no_value=True)
    parser.read(filename)
    for section in parser.sections():
        for param_name in parser.options(section):
            param_val = parser.get(section, param_name)
    return parser

def gen_server_id(ip, port):
    return int("".join(ip.split('.')[-2:]) + str(port))

def gen_conf_for_instance(host, port, data_path,mysql_base):
    mysql_home = '%s/my%s' % (mysql_base, port)
    data_home = '%s/my%s' % (data_path, port)

    return {
        'basedir': mysql_home,
        'port': port,
        'pid_file': '%s/run/mysql.pid' % mysql_home,
        'datadir': data_home,
        'tmpdir': '%s/tmp' % mysql_home,
        'socket': '%s/run/mysql.sock' % mysql_home,
        'log-bin': '%s/log/binlog/binlog' % mysql_home,
        'log_error': '%s/log/error.log' % mysql_home,
        'relay_log': '%s/log/relaylog.log' % mysql_home,
        'relay_log_info_file': '%s/log/relay-log.info' % mysql_home,
        'relay_log_index': '%s/log/relay.index' % mysql_home,
        'slave_load_tmpdir': '%s/tmp' % mysql_home,
        'slow_query_log_file': '%s/log/slow.log' % mysql_home,
        'innodb_data_home_dir': '%s/log/iblog' % mysql_home,
        'innodb_log_group_home_dir': '%s/log/iblog' % mysql_home,
        'server-id': gen_server_id(host, port)
    }

def generate_conf(host,user,password, ssh_port,port, data_path, mysql_base, mysql_home, extra_params):
    """
    :param conf_dict, a dict
    :return:
    """
    mycnf = 'my.cnf_new'
    conf_tmpl = read_cnf_template()
    conf_dict = gen_conf_for_instance(host, port, data_path, mysql_base)

    if not conf_tmpl.has_section('mysqld'):
        conf_tmpl.add_section('mysqld')

    for param_name, param_value in conf_dict.items():
        conf_tmpl.set('mysqld', param_name, param_value)

    for param in extra_params:
        param_name = param['param_name']
        param_value = param['param_value']
        conf_tmpl.set('mysqld', param_name, param_value)

    with open(mycnf, 'w') as cnf:
        conf_tmpl.write(cnf)
    tools.my_log(log_type, '生成配置文件%s！' %mycnf, '')
    sftp_upload_file(host,user,password,ssh_port,mycnf,'%s/my.cnf' %mysql_home)
    tools.my_log(log_type, '上传配置文件至%s/my.cnf！' %mysql_home, '')


def install_default_database(host,user,password,ssh_port,data_path,mysql_base,port,mysql_home):
    # 上传安装包，解压缩
    soft_dir = os.getcwd() + '/frame/mysql_install'
    soft_name = 'mysql-5.7.24-linux-glibc2.12-x86_64.tar.gz'
    local_soft = '%s/%s' %(soft_dir,soft_name)
    remote_loc = '%s/%s' %(mysql_base,soft_name)
    sftp_upload_file(host,user,password,ssh_port,local_soft,remote_loc)
    tools.my_log(log_type, '上传安装文件至%s！' %remote_loc, '')
    cmd = 'tar -xzvf %s -C %s' %(remote_loc,mysql_base)
    exec_command(host,user,password,ssh_port,cmd)
    tools.my_log(log_type, '解压缩完成%s！' %remote_loc, '')
    cmd = 'mv %s/mysql*/* %s' %(mysql_base,mysql_home)
    exec_command(host,user,password,ssh_port,cmd)
    # 建用户，授权
    cmd = '/usr/bin/groupadd mysql'
    exec_command(host,user,password,ssh_port,cmd)
    cmd = '/usr/bin/useradd -d /home/mysql -g mysql -m mysql'
    exec_command(host,user,password,ssh_port,cmd)
    tools.my_log(log_type, '创建MySQL用户成功！', '')
    cmd = 'chown -R mysql:mysql %s' % mysql_base
    exec_command(host,user,password,ssh_port,cmd)
    cmd = 'chown -R mysql:mysql %s/my%s' %(data_path,port)
    exec_command(host,user,password,ssh_port,cmd)
    # 初始化MySQL
    cmd = '%s/bin/mysqld --defaults-file=%s/my.cnf --initialize-insecure --user=mysql' %(mysql_home,mysql_home)
    exec_command(host,user,password,ssh_port,cmd)
    tools.my_log(log_type, '初始化MySQL数据库成功！', '')
    # 启动MySQL数据库
    cmd = '%s/bin/mysqld_safe --defaults-file=%s/my.cnf --user=mysql &' %(mysql_home,mysql_home)
    # exec_command(host,user,password,cmd)
    tools.my_log(log_type, "创建MySQL：%s:%s成功，初始密码为空，请运行%s启动MySQL数据库！" %(host,port,cmd), '')


def mysql_install(host,user,password,ssh_port,data_path,mysql_base,port):
    tools.mysql_exec("delete from many_logs where log_type = 'MySQL部署'", '')
    extra_params = ''
    mysql_home = '/%s/my%s' %(mysql_base,port)
    # 1. 创建目录
    tools.my_log(log_type, '开始创建目录！', '')
    create_home_dir(host,user,password,ssh_port,port,data_path,mysql_base)
    # 2. 生成配置文件
    tools.my_log(log_type, '生成配置文件！', '')
    generate_conf(host,user,password,ssh_port,port,data_path,mysql_base,mysql_home,extra_params)
    # 3. 初始化数据库
    install_default_database(host,user,password,ssh_port,data_path,mysql_base,port,mysql_home)

if __name__  == '__main__':
    host='192.168.48.51'
    user= 'root'
    password= 'mysqld'
    data_path = '/data'
    mysql_base = '/u01'
    port = 3307
    mysql_install(host ,user,password,data_path,mysql_base,port)

