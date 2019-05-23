#! /usr/bin/python
# encoding:utf-8

import os
import paramiko
import re
import time

def os_get_data(host,user,password):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(host, 22, user, password)
    std_in_net, std_out_net, std_err_net = ssh_client.exec_command('cat /proc/net/dev')
    std_in_cpu, std_out_cpu, std_err_cpu = ssh_client.exec_command('cat /proc/stat | grep "cpu "')

    stdout_net = std_out_net.read().decode()
    stderr_net = std_err_net.read().decode()

    stdout_cpu = std_out_cpu.read().decode()
    stderr_cpu = std_err_cpu.read().decode()

    if stderr_net != "":
        print(stderr_net)
    else:
        list_net = stdout_net.split('\n')
        for each_net in list_net:
            if each_net.find('eth0') > 0:
                list_eth0 = each_net.split(":")[1]
                recv = float(list_eth0.split()[0])
                send = float(list_eth0.split()[8])

        list_eth0 = list_net[3].split(":")[1]
        recv = float(list_eth0.split()[0])
        send = float(list_eth0.split()[8])

    if stderr_cpu != "":
        print(stderr_cpu)
    else:
        cpu_time_list = re.findall('\d+', stdout_cpu)
        cpu_idle = cpu_time_list[3]
        total_cpu_time = 0
        for t in cpu_time_list:
            total_cpu_time = total_cpu_time + int(t)
    return (recv, send ,total_cpu_time,cpu_idle)

# 网卡流量，CPU使用率
def os_get_info(host,user,password):
    # 第一次采集
    recv_first,send_first,total_cpu_time1,cpu_idle1 = os_get_data(host,user,password)
    time.sleep(1)
    # 第二次采集
    recv_second,send_second,total_cpu_time2,cpu_idle2 = os_get_data(host,user,password)

    recv_data = round((recv_second - recv_first)/1024,2)
    send_data = round((send_second - send_first)/1024,2)

    cpu_usage = round(1 - (float(cpu_idle2) - float(cpu_idle1)) / (float(total_cpu_time2) - float(total_cpu_time1)), 2)

    return(recv_data,send_data,cpu_usage)

if __name__ == '__main__':
    print os_get_info('192.168.48.10','root','oracle')

# 获取内存使用率
def os_get_mem(host,ssh_port,user,password):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(host, ssh_port, user, password)
    std_in, std_out, std_err = ssh_client.exec_command('cat /proc/meminfo')

    stdout = std_out.read().decode()
    stderr = std_err.read().decode()

    if stderr != "":
        print(stderr)

    # 使用MemTotal匹配
    str_total = re.search('MemTotal:.*?\n', stdout).group()
    # 使用/d(空格匹配)
    totalmem = re.search('\d+',str_total).group()

    str_free = re.search('MemFree:.*?\n', stdout).group()
    str_cached = re.search('Cached:.*?\n', stdout).group()
    str_buffers = re.search('Buffers:.*?\n', stdout).group()
    freemem = re.search('\d+',str_free).group()
    cached = re.search('\d+', str_cached).group()
    buffers = re.search('\d+', str_buffers).group()

    use = 1 - round((float(freemem)+float(cached)+float(buffers))/float(totalmem), 2)

    # print('当前内存使用率为：'+ str(use))
    return use*100


# 获取文件系统使用率
def os_get_disk(host,ssh_port,user,password):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(host, ssh_port, user, password)
    std_in, std_out, std_err = ssh_client.exec_command('df -h')

    stdout = std_out.read().decode()
    stderr = std_err.read().decode()

    if stderr != "":
        print(stderr)

    list_disk =  stdout.split('\n')
    l_disk = []
    for i in xrange(len(list_disk)):
        str_disk = str(list_disk[i].encode('utf-8'))
        if str_disk.startswith('/dev') and str_disk.split()[5]<>'/boot':
            d = {}
            d['name'] = str_disk.split()[5]
            d['size'] = str_disk.split()[1]
            d['avail'] = str_disk.split()[3]
            d['used'] = str_disk.split()[4]
            d['filesystem'] = str_disk.split()[0]
            l_disk.append(d)
    return l_disk



'''if __name__ == '__main__':
    os_get_mem('192.168.48.10','root','oracle')
    disk_use = os_get_disk('192.168.48.10','root','oracle')
    print disk_use'''
