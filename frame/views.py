#! /usr/bin/python
# encoding:utf-8

import os
import json

from django.shortcuts import render,render_to_response,RequestContext
from django.http import HttpResponse, HttpResponseRedirect

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# Create your views here.
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from django.contrib import messages

import datetime
from frame import tools
# 配置文件
import ConfigParser
import base64
import frame.models as models_frame
import linux_mon.models as models_linux
import oracle_mon.models as models_oracle
import mysql_mon.models as models_mysql
import redis_mon.models as models_redis


import easy_check as easy_check
import log_collect as collect
import easy_start as start
import tasks as task

import commands

# Create your views here.

@login_required(login_url='/login')
def show_all(request):
    # 资产状况统计
    linux_all_cnt = len(models_linux.TabLinuxServers.objects.all())
    linux_seccess_cnt = len(models_linux.LinuxRate.objects.filter(linux_rate_level='success'))
    linux_warning_cnt = len(models_linux.LinuxRate.objects.filter(linux_rate_level='warning'))
    linux_danger_cnt = len(models_linux.LinuxRate.objects.filter(linux_rate_level='danger'))
    ora_all_cnt = len(models_oracle.TabOracleServers.objects.all())
    ora_seccess_cnt = len(models_oracle.OracleDbRate.objects.filter(db_rate_level='success'))
    ora_warning_cnt = len(models_oracle.OracleDbRate.objects.filter(db_rate_level='warning'))
    ora_danger_cnt = len(models_oracle.OracleDbRate.objects.filter(db_rate_level='danger'))
    msql_all_cnt = len(models_mysql.TabMysqlServers.objects.all())
    msql_seccess_cnt = len(models_mysql.MysqlDbRate.objects.filter(db_rate_level='success'))
    msql_warning_cnt = len(models_mysql.MysqlDbRate.objects.filter(db_rate_level='warning'))
    msql_danger_cnt = len(models_mysql.MysqlDbRate.objects.filter(db_rate_level='danger'))
    # 告警
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    alarm_range_default = '1小时'.decode("utf-8")
    alarm_begin_time = tools.range(alarm_range_default)

    # 告警统计
    break_cnt = len(models_frame.TabAlarmInfoHis.objects.filter(alarm_type__contains='通断').filter(alarm_time__gt=alarm_begin_time))
    res_cnt = len(models_frame.TabAlarmInfoHis.objects.filter(alarm_type__contains='使用率').filter(alarm_time__gt=alarm_begin_time))
    perf_cnt = len(models_frame.TabAlarmInfoHis.objects.filter(alarm_type__contains='性能').filter(alarm_time__gt=alarm_begin_time))
    wait_cnt = len(models_frame.TabAlarmInfoHis.objects.filter(alarm_type__contains='锁').filter(alarm_time__gt=alarm_begin_time))
    invalid_cnt = len(models_frame.TabAlarmInfoHis.objects.filter(alarm_type__contains='失效').filter(alarm_time__gt=alarm_begin_time))
    delay_cnt = len(models_frame.TabAlarmInfoHis.objects.filter(alarm_type__contains='延迟').filter(alarm_time__gt=alarm_begin_time))
    expire_cnt = len(models_frame.TabAlarmInfoHis.objects.filter(alarm_type__contains='过期').filter(alarm_time__gt=alarm_begin_time))
    logerr_cnt = len(models_frame.TabAlarmInfoHis.objects.filter(alarm_type__contains='日志').filter(alarm_time__gt=alarm_begin_time))

    # top5
    top_5_cpu = models_linux.OsInfo.objects.filter(cpu_used__isnull=False).order_by("-cpu_used")[:5]
    top_5_mem = models_linux.OsInfo.objects.filter(mem_used__isnull=False).order_by("-mem_used")[:5]
    top_5_disk = models_linux.OsFilesystem.objects.filter(pct_used__isnull=False).order_by("-pct_used")[:5]
    # 当前时间
    now = tools.now()
    if request.method == 'POST':
        logout(request)
        return HttpResponseRedirect('/login/')
    if messageinfo_list:
        msg_num = len(messageinfo_list)
        msg_last = models_frame.TabAlarmInfo.objects.latest('id')
        msg_last_content = msg_last.alarm_content
        tim_last = (datetime.datetime.now() - msg_last.alarm_time).seconds / 60
    else:
        msg_num = 0
        msg_last_content = ''
        tim_last = ''
    return render_to_response('frame/dashboard.html',
                              {'messageinfo_list': messageinfo_list, 'linux_all_cnt': linux_all_cnt,
                               'linux_seccess_cnt': linux_seccess_cnt, 'linux_warning_cnt': linux_warning_cnt,
                               'linux_danger_cnt': linux_danger_cnt, 'ora_all_cnt': ora_all_cnt,
                               'ora_seccess_cnt': ora_seccess_cnt, 'ora_warning_cnt': ora_warning_cnt,
                               'ora_danger_cnt': ora_danger_cnt,
                               'msql_all_cnt': msql_all_cnt, 'msql_seccess_cnt': msql_seccess_cnt,
                               'msql_warning_cnt': msql_warning_cnt, 'msql_danger_cnt': msql_danger_cnt,
                               'msg_num': msg_num, 'top_5_cpu': top_5_cpu, 'top_5_mem': top_5_mem,'top_5_disk':top_5_disk, 'now': now,
                               'msg_last_content': msg_last_content, 'tim_last': tim_last,
                               'break_cnt':break_cnt,'res_cnt':res_cnt,'perf_cnt':perf_cnt,'wait_cnt':wait_cnt,'invalid_cnt':invalid_cnt,
                               'delay_cnt':delay_cnt,'expire_cnt':expire_cnt,'logerr_cnt':logerr_cnt})



@login_required(login_url='/login')
def mon_servers(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    # linux监控设备
    linux_servers_list = models_linux.TabLinuxServers.objects.all()
    # Oracle监控设备
    oracle_servers_list = models_oracle.TabOracleServers.objects.all()
    # Mysql监控设备
    mysql_servers_list = models_mysql.TabMysqlServers.objects.all()
    # Mysql监控设备
    redis_mon_list = models_redis.RedisMonConf.objects.all()

    if request.method == 'POST':
        logout(request)
        return HttpResponseRedirect('/login/')

    if messageinfo_list:
        msg_num = len(messageinfo_list)
        msg_last = models_frame.TabAlarmInfo.objects.latest('id')
        msg_last_content = msg_last.alarm_content
        tim_last = (datetime.datetime.now() - msg_last.alarm_time).seconds / 60
    else:
        msg_num = 0
        msg_last_content = ''
        tim_last = ''
    return render_to_response('frame/mon_servers.html',
                              {'linux_servers_list': linux_servers_list, 'oracle_servers_list': oracle_servers_list,
                               'mysql_servers_list': mysql_servers_list, 'redis_mon_list': redis_mon_list,
                               'messageinfo_list': messageinfo_list, 'msg_num': msg_num,
                               'msg_last_content': msg_last_content, 'tim_last': tim_last})


@login_required(login_url='/login')
def alarm_setting(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    # 告警策略
    alarm_list = models_frame.TabAlarmConf.objects.all().order_by('server_type')

    if request.method == 'POST':
        logout(request)
        return HttpResponseRedirect('/login/')

    if messageinfo_list:
        msg_num = len(messageinfo_list)
        msg_last = models_frame.TabAlarmInfo.objects.latest('id')
        msg_last_content = msg_last.alarm_content
        tim_last = (datetime.datetime.now() - msg_last.alarm_time).seconds / 60
    else:
        msg_num = 0
        msg_last_content = ''
        tim_last = ''
    return render_to_response('frame/alarm_setting.html',
                              {'alarm_list': alarm_list, 'messageinfo_list': messageinfo_list, 'msg_num': msg_num,
                               'msg_last_content': msg_last_content, 'tim_last': tim_last})


@login_required(login_url='/login')
def alarm_settings_edit(request):
    status = 0
    rid = request.GET.get('id')
    alarm_setting_edit = models_frame.TabAlarmConf.objects.get(id=rid)
    if request.method == "POST":
        if request.POST.has_key('commit'):
            judge = request.POST.get('judge', None)
            jdg_value = request.POST.get('jdg_value', None)
            jdg_des = request.POST.get('jdg_des', None)
            select_sql = request.POST.get('select_sql', None)
            jdg_sql = request.POST.get('jdg_sql', None)
            models_frame.TabAlarmConf.objects.filter(id=rid).update(judge = judge,jdg_value = jdg_value,
                                                                    jdg_des = jdg_des,select_sql=select_sql,jdg_sql=jdg_sql)
            status = 1
        elif request.POST.has_key('logout'):
            logout(request)
            return HttpResponseRedirect('/login/')

    return render_to_response('frame/alarm_settings_edit.html', {'alarm_setting_edit': alarm_setting_edit, 'status':status})


@login_required(login_url='/login')
def linux_servers_edit(request):
    status = 0
    rid = request.GET.get('id')
    linux_server_edit = models_linux.TabLinuxServers.objects.get(id=rid)
    if request.method == "POST":
        if request.POST.has_key('commit'):
            tags = request.POST.get('tags', None)
            host_name = request.POST.get('host_name', None)
            host = request.POST.get('host', None)
            user = request.POST.get('user', None)
            password = base64.encodestring(request.POST.get('password', None))
            ssh_port = request.POST.get('ssh_port', None)
            connect = request.POST.get('connect', None)
            connect = tools.isno(connect)
            cpu = request.POST.get('cpu', None)
            cpu = tools.isno(cpu)
            mem = request.POST.get('mem', None)
            mem = tools.isno(mem)
            swap = request.POST.get('swap', None)
            swap = tools.isno(swap)
            disk = request.POST.get('disk', None)
            disk = tools.isno(disk)
            models_linux.TabLinuxServers.objects.filter(id=rid).update(tags=tags,host_name=host_name, host=host, user=user,
                                                                 password=password,ssh_port=ssh_port,
                                                                 connect=connect,
                                                                 cpu=cpu, mem=mem,swap=swap,disk=disk)
            status = 1
        elif request.POST.has_key('logout'):
            logout(request)
            return HttpResponseRedirect('/login/')

    return render_to_response('linux_mon/linux_servers_edit.html', {'linux_server_edit': linux_server_edit, 'status':status})

@login_required(login_url='/login')
def linux_servers_add(request):
    status = 0
    if request.method == "POST":
        if request.POST.has_key('commit'):
            tags = request.POST.get('tags', None)
            host_name = request.POST.get('host_name', None)
            host = request.POST.get('host', None)
            user = request.POST.get('user', None)
            password = base64.encodestring(request.POST.get('password', None))
            ssh_port = request.POST.get('ssh_port', None)
            connect = request.POST.get('connect', None)
            connect = tools.isno(connect)
            cpu = request.POST.get('cpu', None)
            cpu = tools.isno(cpu)
            mem = request.POST.get('mem', None)
            mem = tools.isno(mem)
            swap = request.POST.get('swap', None)
            swap = tools.isno(swap)
            disk = request.POST.get('disk', None)
            disk = tools.isno(disk)
            models_linux.TabLinuxServers.objects.create(tags=tags,host_name=host_name, host=host, user=user, password=password,ssh_port=ssh_port,
                                                  connect=connect, cpu=cpu, mem=mem, swap=swap,disk=disk )
            status = 1
        elif request.POST.has_key('logout'):
            logout(request)
            return HttpResponseRedirect('/login/')

    return render_to_response('linux_mon/linux_servers_add.html', {'status':status})

@login_required(login_url='/login')
def linux_servers_del(request):
    rid = request.GET.get('id')
    models_linux.TabLinuxServers.objects.filter(id=rid).delete()
    return HttpResponseRedirect('/mon_servers/')

@login_required(login_url='/login')
def oracle_servers_add(request):
    status = 0
    if request.method == "POST":
        if request.POST.has_key('commit'):
            tags = request.POST.get('tags', None)
            host = request.POST.get('host', None)
            port = request.POST.get('port', None)
            version = request.POST.get('version', None)
            service_name = request.POST.get('service_name', None)
            user = request.POST.get('user', None)
            password = base64.encodestring(request.POST.get('password', None))
            service_name_cdb = request.POST.get('service_name_cdb', None)
            user_cdb = request.POST.get('user_cdb', None)
            password_cdb = base64.encodestring(request.POST.get('password_cdb', None))
            user_os = request.POST.get('user_os', None)
            password_os = base64.encodestring(request.POST.get('password_os', None))
            ssh_port_os = request.POST.get('ssh_port_os', None)
            connect = request.POST.get('connect', None)
            connect = tools.isno(connect)
            tbs = request.POST.get('tbs', None)
            tbs = tools.isno(tbs)
            adg = request.POST.get('adg', None)
            adg = tools.isno(adg)
            temp_tbs = request.POST.get('temp_tbs', None)
            temp_tbs = tools.isno(temp_tbs)
            undo_tbs = request.POST.get('undo_tbs', None)
            undo_tbs = tools.isno(undo_tbs)
            conn = request.POST.get('conn', None)
            conn = tools.isno(conn)
            err_info = request.POST.get('err_info', None)
            err_info = tools.isno(err_info)
            invalid_index = request.POST.get('invalid_index', None)
            invalid_index = tools.isno(invalid_index)
            oracle_lock = request.POST.get('oracle_lock', None)
            oracle_lock = tools.isno(oracle_lock)
            oracle_pwd = request.POST.get('oracle_pwd', None)
            oracle_pwd = tools.isno(oracle_pwd)
            oracle_event = request.POST.get('oracle_event', None)
            oracle_event = tools.isno(oracle_event)
            oracle_pga = request.POST.get('oracle_pga', None)
            oracle_pga = tools.isno(oracle_pga)
            oracle_archive = request.POST.get('oracle_archive', None)
            oracle_archive = tools.isno(oracle_archive)
            models_oracle.TabOracleServers.objects.create(tags=tags,host=host, port=port, version=version,service_name=service_name,
                                                   user=user, password=password,service_name_cdb=service_name_cdb,
                                                   user_cdb=user_cdb, password_cdb=password_cdb,
                                                   user_os=user_os, password_os=password_os, ssh_port_os=ssh_port_os,connect=connect,
                                                   tbs=tbs,
                                                   adg=adg, temp_tbs=temp_tbs,
                                                   undo_tbs=undo_tbs,
                                                   conn=conn, err_info=err_info,invalid_index=invalid_index,
                                                   oracle_lock =oracle_lock,oracle_pwd =oracle_pwd,
                                                   oracle_event=oracle_event,pga=oracle_pga,archive=oracle_archive)
            status = 1
        elif request.POST.has_key('logout'):
            logout(request)
            return HttpResponseRedirect('/login/')

    return render_to_response('oracle_mon/oracle_servers_add.html', {'status':status})

@login_required(login_url='/login')
def oracle_servers_del(request):
    rid = request.GET.get('id')
    models_oracle.TabOracleServers.objects.filter(id=rid).delete()
    return HttpResponseRedirect('/mon_servers/')

@login_required(login_url='/login')
def oracle_servers_edit(request):
    status = 0
    rid = request.GET.get('id')
    oracle_server_edit = models_oracle.TabOracleServers.objects.get(id=rid)
    if request.method == "POST":
        if request.POST.has_key('commit'):
            tags = request.POST.get('tags', None)
            host = request.POST.get('host', None)
            port = request.POST.get('port', None)
            version = request.POST.get('version', None)
            service_name = request.POST.get('service_name', None)
            user = request.POST.get('user', None)
            password = request.POST.get('password', None)
            password_value = models_oracle.TabOracleServers.objects.values("password").filter(id=rid)[0]
            if  password.encode('utf-8') + '\n'  != password_value['password'].encode('utf-8'):
                password = base64.encodestring(request.POST.get('password', None))
            user_os = request.POST.get('user_os', None)
            password_os = request.POST.get('password_os', None)
            password_os_value =  models_oracle.TabOracleServers.objects.values("password_os").filter(id=rid)[0]
            if  password_os.encode('utf-8') + '\n'  != password_os_value['password_os'].encode('utf-8'):
                password_os = base64.encodestring(request.POST.get('password_os', None))
            ssh_port_os = request.POST.get('ssh_port_os', None)
            service_name_cdb = request.POST.get('service_name_cdb', None)
            user_cdb = request.POST.get('user_cdb', None)
            password_cdb = request.POST.get('password_cdb', None)
            password_cdb_value = models_oracle.TabOracleServers.objects.values("password_cdb").filter(id=rid)[0]
            if password_cdb.encode('utf-8') + '\n' != password_cdb_value['password_cdb'].encode('utf-8'):
                password_cdb = base64.encodestring(request.POST.get('password_cdb', None))
            connect = request.POST.get('connect', None)
            connect = tools.isno(connect)
            tbs = request.POST.get('tbs', None)
            tbs = tools.isno(tbs)
            adg = request.POST.get('adg', None)
            adg = tools.isno(adg)
            temp_tbs = request.POST.get('temp_tbs', None)
            temp_tbs = tools.isno(temp_tbs)
            undo_tbs = request.POST.get('undo_tbs', None)
            undo_tbs = tools.isno(undo_tbs)
            conn = request.POST.get('conn', None)
            conn = tools.isno(conn)
            err_info = request.POST.get('err_info', None)
            err_info = tools.isno(err_info)
            invalid_index = request.POST.get('invalid_index', None)
            invalid_index = tools.isno(invalid_index)
            oracle_lock = request.POST.get('oracle_lock', None)
            oracle_lock = tools.isno(oracle_lock)
            oracle_pwd = request.POST.get('oracle_pwd', None)
            oracle_pwd = tools.isno(oracle_pwd)
            oracle_event = request.POST.get('oracle_event', None)
            oracle_event = tools.isno(oracle_event)
            oracle_pga = request.POST.get('oracle_pga', None)
            oracle_pga = tools.isno(oracle_pga)
            oracle_archive = request.POST.get('oracle_archive', None)
            oracle_archive = tools.isno(oracle_archive)
            models_oracle.TabOracleServers.objects.filter(id=rid).update(tags=tags,host=host, port=port, version=version,service_name=service_name,
                                                                  user=user, password=password,service_name_cdb=service_name_cdb,
                                                                  user_os=user_os, password_os=password_os,ssh_port_os=ssh_port_os,
                                                                         user_cdb=user_cdb,password_cdb=password_cdb,
                                                                  connect=connect,tbs=tbs,temp_tbs=temp_tbs,
                                                                  undo_tbs=undo_tbs, conn=conn, err_info=err_info,
                                                                  invalid_index=invalid_index,
                                                          oracle_lock =oracle_lock,oracle_pwd =oracle_pwd,
                                                          oracle_event=oracle_event,pga=oracle_pga,archive=oracle_archive)
            status = 1
        elif request.POST.has_key('logout'):
            logout(request)
            return HttpResponseRedirect('/login/')

    return render_to_response('oracle_mon/oracle_servers_edit.html', {'oracle_server_edit': oracle_server_edit, 'status':status})

@login_required(login_url='/login')
def mysql_servers_add(request):
    status = 0
    if request.method == "POST":
        if request.POST.has_key('commit'):
            tags = request.POST.get('tags', None)
            host = request.POST.get('host', None)
            port = request.POST.get('port', None)
            user = request.POST.get('user', None)
            password = base64.encodestring(request.POST.get('password', None))
            user_os = request.POST.get('user_os', None)
            password_os = base64.encodestring(request.POST.get('password_os', None))
            ssh_port_os = request.POST.get('ssh_port_os', None)
            connect = request.POST.get('connect', None)
            connect = tools.isno(connect)
            repl = request.POST.get('repl', None)
            repl = tools.isno(repl)
            conn = request.POST.get('conn', None)
            conn = tools.isno(conn)
            err_info = request.POST.get('err_info', None)
            err_info = tools.isno(err_info)
            models_mysql.TabMysqlServers.objects.create(host=host, port=port, tags=tags,
                                                   user=user, password=password,
                                                   user_os=user_os, password_os=password_os,
                                                   ssh_port_os=ssh_port_os,connect=connect,
                                                   repl=repl,conn=conn, err_info=err_info,)
            status = 1
        elif request.POST.has_key('logout'):
            logout(request)
            return HttpResponseRedirect('/login/')

    return render_to_response('mysql_mon/mysql_servers_add.html', {'status':status})

@login_required(login_url='/login')
def mysql_servers_del(request):
    rid = request.GET.get('id')
    models_mysql.TabMysqlServers.objects.filter(id=rid).delete()
    return HttpResponseRedirect('/mon_servers/')

@login_required(login_url='/login')
def mysql_servers_edit(request):
    status = 0
    rid = request.GET.get('id')
    mysql_server_edit = models_mysql.TabMysqlServers.objects.get(id=rid)
    if request.method == "POST":
        if request.POST.has_key('commit'):
            tags = request.POST.get('tags', None)
            host = request.POST.get('host', None)
            port = request.POST.get('port', None)
            user = request.POST.get('user', None)
            password = request.POST.get('password', None)
            password_value = models_mysql.TabMysqlServers.objects.values("password").filter(id=rid)[0]
            if password.encode('utf-8') + '\n' != password_value['password'].encode('utf-8'):
                password = base64.encodestring(request.POST.get('password', None))
            user_os = request.POST.get('user_os', None)
            password_os = request.POST.get('password_os', None)
            password_os_value = models_mysql.TabMysqlServers.objects.values("password_os").filter(id=rid)[0]
            if password_os.encode('utf-8') + '\n' != password_os_value['password_os'].encode('utf-8'):
                password_os = base64.encodestring(request.POST.get('password_os', None))
            ssh_port_os = request.POST.get('ssh_port_os', None)
            connect = request.POST.get('connect', None)
            connect = tools.isno(connect)
            repl = request.POST.get('repl', None)
            repl = tools.isno(repl)
            conn = request.POST.get('conn', None)
            conn = tools.isno(conn)
            err_info = request.POST.get('err_info', None)
            err_info = tools.isno(err_info)
            models_mysql.TabMysqlServers.objects.filter(id=rid).update(tags=tags,host=host, port=port,
                                                                  user=user, password=password,
                                                                  user_os=user_os, password_os=password_os,ssh_port_os=ssh_port_os,
                                                                  connect=connect,
                                                                  repl=repl,
                                                                  conn=conn, err_info=err_info)
            status = 1

        elif request.POST.has_key('logout'):
            logout(request)
            return HttpResponseRedirect('/login/')

    return render_to_response('mysql_mon/mysql_servers_edit.html', {'mysql_server_edit': mysql_server_edit, 'status':status})

@login_required(login_url='/login')
def show_alarm(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()

    if request.POST.has_key('logout'):
        logout(request)
        return HttpResponseRedirect('/login/')

    if messageinfo_list:
        msg_num = len(messageinfo_list)
        msg_last = models_frame.TabAlarmInfo.objects.latest('id')
        msg_last_content = msg_last.alarm_content
        tim_last = (datetime.datetime.now() - msg_last.alarm_time).seconds / 60
    else:
        msg_num = 0
        msg_last_content = ''
        tim_last = ''
    return render_to_response('frame/show_alarm.html', {'messageinfo_list': messageinfo_list, 'msg_num': msg_num,
                                                  'msg_last_content': msg_last_content, 'tim_last': tim_last})


@login_required(login_url='/login')
def recorder(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    sys_nums =  len(models_frame.EventRecorder.objects.filter(event_section='系统'))
    db_nums =  len(models_frame.EventRecorder.objects.filter(event_section='数据库'))
    other_nums =  len(models_frame.EventRecorder.objects.filter(event_section='其他'))
    err_nums =  len(models_frame.EventRecorder.objects.filter(event_type='故障'))
    chg_nums =  len(models_frame.EventRecorder.objects.filter(event_type='变更'))
    upg_nums =  len(models_frame.EventRecorder.objects.filter(event_type='升级'))

    server_type =  request.GET.get('server_type')
    rec_type = request.GET.get('rec_type')

    if server_type == 'None':
        server_type = ''
    if rec_type == 'None':
        rec_type = ''

    if server_type and not rec_type:
        server_type = server_type.encode("utf-8")
        recorder_list = models_frame.EventRecorder.objects.filter(event_section=server_type).order_by('-record_time')
    elif rec_type and not server_type:
        rec_type = rec_type.encode("utf-8")
        recorder_list = models_frame.EventRecorder.objects.filter(event_type=rec_type).order_by('-record_time')
    elif server_type and rec_type:
        server_type = server_type.encode("utf-8")
        rec_type = rec_type.encode("utf-8")
        recorder_list = models_frame.EventRecorder.objects.filter(event_type=rec_type,event_section=server_type).order_by('-record_time')
    else:
        recorder_list = models_frame.EventRecorder.objects.order_by('-record_time')
    all_nums = len(recorder_list)

    if request.method == 'POST':
        logout(request)
        return HttpResponseRedirect('/login/')
    if messageinfo_list:
        msg_num = len(messageinfo_list)
        msg_last = models_frame.TabAlarmInfo.objects.latest('id')
        msg_last_content = msg_last.alarm_content
        tim_last = (datetime.datetime.now() - msg_last.alarm_time).seconds / 60
    else:
        msg_num = 0
        msg_last_content = ''
        tim_last = ''
    return render_to_response('frame/recorder.html',
                              {'recorder_list': recorder_list, 'all_nums': all_nums, 'sys_nums': sys_nums,
                               'db_nums': db_nums, 'other_nums': other_nums,
                               'err_nums': err_nums, 'chg_nums': chg_nums, 'upg_nums': upg_nums,
                               'messageinfo_list': messageinfo_list,
                               'msg_num': msg_num, 'msg_last_content': msg_last_content, 'tim_last': tim_last,
                               'server_type':server_type,'rec_type':rec_type })


@login_required(login_url='/login')
def recorder_del(request):
    rid = request.GET.get('id')
    models_frame.EventRecorder.objects.filter(id=rid).delete()
    return HttpResponseRedirect('/recorder/')


@login_required(login_url='/login')
def recorder_add(request):
    status = 0
    recorder_list = models_frame.EventRecorder.objects.order_by('record_time')
    all_nums = len(recorder_list)
    sys_nums =  len(models_frame.EventRecorder.objects.filter(event_section='系统'))
    db_nums =  len(models_frame.EventRecorder.objects.filter(event_section='数据库'))
    other_nums =  len(models_frame.EventRecorder.objects.filter(event_section='其他'))
    err_nums =  len(models_frame.EventRecorder.objects.filter(event_type='故障'))
    chg_nums =  len(models_frame.EventRecorder.objects.filter(event_type='变更'))
    upg_nums =  len(models_frame.EventRecorder.objects.filter(event_type='升级'))
    if request.method == "POST":
        if request.POST.has_key('commit'):
            event_section = request.POST.get('event_section', None)
            event_type = request.POST.get('event_type', None)
            if event_type == unicode('升级', 'utf-8'):
                event_type_color = 'success'
            elif event_type == unicode('变更', 'utf-8'):
                event_type_color = 'warning'
            else:
                event_type_color = 'danger'
            event_content = request.POST.get('event_content', None)
            models_frame.EventRecorder.objects.create(event_section=event_section, event_type=event_type,
                                                event_type_color=event_type_color, event_content=event_content)
            status = 1
        elif request.POST.has_key('logout'):
            logout(request)
            return HttpResponseRedirect('/login/')


    return render_to_response('frame/recorder_add.html',
                              {'recorder_list': recorder_list, 'all_nums': all_nums, 'sys_nums': sys_nums,
                                   'db_nums': db_nums, 'other_nums': other_nums,
                                   'err_nums': err_nums, 'chg_nums': chg_nums, 'upg_nums': upg_nums,'status':status})



@login_required(login_url='/login')
def sys_setting(request):
    # 读配置文件
    conf = ConfigParser.ConfigParser()
    conf_path = os.getcwd() + '/config/db_monitor.conf'
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    now = tools.now()
    conf.read(conf_path)
    # 告警邮件
    sender = conf.get("email", "sender")
    smtpserver = conf.get("email", "smtpserver")
    username = conf.get("email", "username")
    password_email = conf.get("email", "password")
    receiver = conf.get("email", "receiver")
    msg_from = conf.get("email", "msg_from")
    is_send = conf.get("email", "is_send")
    # 采集周期
    check_sleep_time = conf.get("policy", "check_sleep_time")
    alarm_sleep_time = conf.get("policy", "alarm_sleep_time")
    next_send_email_time = conf.get("policy", "next_send_email_time")
   # 监控数据存放
    host = conf.get("target_mysql", "host")
    port = conf.get("target_mysql", "port")
    user = conf.get("target_mysql", "user")
    password_mysql = conf.get("target_mysql", "password")
    dbname = conf.get("target_mysql", "dbname")

    if request.method == 'POST':
        # 修改邮箱设置
        if request.POST.has_key('commit_email'):
            sender = request.POST.get('sender', None)
            smtpserver = request.POST.get('smtpserver', None)
            username = request.POST.get('username', None)
            password_email = request.POST.get('password_email', None)
            receiver = request.POST.get('receiver', None)
            msg_from = request.POST.get('msg_from', None)
            conf.set("email","sender",sender)
            conf.set("email", "smtpserver", smtpserver)
            conf.set("email", "username", username)
            conf.set("email", "password_email", password_email)
            conf.set("email", "receiver", receiver)
            conf.set("email", "msg_from", msg_from)
            check_box = request.POST.get('check_box')
            if check_box:
                conf.set("email", "is_send", '1')
            else:
                conf.set("email", "is_send", '0')
            conf.write(open(conf_path, "w"))
            return HttpResponseRedirect('/sys_setting/')
        # 修改采集周期设置
        elif request.POST.has_key('commit_check'):
            check_sleep_time = request.POST.get('check_sleep_time', None)
            alarm_sleep_time = request.POST.get('alarm_sleep_time', None)
            next_send_email_time = request.POST.get('next_send_email_time', None)
            conf.set("policy", "check_sleep_time", check_sleep_time)
            conf.set("policy", "alarm_sleep_time", alarm_sleep_time)
            conf.set("policy", "next_send_email_time", next_send_email_time)
            conf.write(open(conf_path, "w"))
            return HttpResponseRedirect('/sys_setting/')
        # 修改数据库设置
        elif request.POST.has_key('commit_db'):
            host = request.POST.get('host', None)
            port = request.POST.get('port', None)
            user = request.POST.get('user', None)
            password_mysql = request.POST.get('password_mysql', None)
            dbname = request.POST.get('dbname', None)
            conf.set("target_mysql", "host", host)
            conf.set("target_mysql", "user", user)
            conf.set("target_mysql", "port", port)
            conf.set("target_mysql", "password", password_mysql)
            conf.set("target_mysql", "dbname", dbname)
            conf.write(open(conf_path, "w"))
            return HttpResponseRedirect('/sys_setting/')

        elif request.POST.has_key('logout'):
            logout(request)
            return HttpResponseRedirect('/login/')

    if messageinfo_list:
        msg_num = len(messageinfo_list)
        msg_last = models_frame.TabAlarmInfo.objects.latest('id')
        msg_last_content = msg_last.alarm_content
        tim_last = (datetime.datetime.now() - msg_last.alarm_time).seconds / 60
    else:
        msg_num = 0
        msg_last_content = ''
        tim_last = ''
    return render_to_response('frame/sys_setting.html',
                              {'messageinfo_list': messageinfo_list, 'msg_num': msg_num,
                               'msg_last_content': msg_last_content, 'tim_last': tim_last,
                               'sender': sender, 'smtpserver': smtpserver, 'username': username,
                               'password_email': password_email, 'receiver': receiver, 'msg_from': msg_from,
                               'check_sleep_time': check_sleep_time, 'alarm_sleep_time': alarm_sleep_time,
                               'next_send_email_time': next_send_email_time, 'host': host, 'port': port, 'user': user,
                               'password_mysql': password_mysql, 'dbname': dbname, 'now': now,'is_send':is_send})


@login_required(login_url='/login')
def my_check(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()

    linuxtagsinfo = models_linux.TabLinuxServers.objects.all().order_by('tags')
    oracletagsinfo = models_oracle.TabOracleServers.objects.all().order_by('tags')
    mysqltagsinfo = models_mysql.TabMysqlServers.objects.all().order_by('tags')

    select_type = request.GET.get('select_type')
    if not select_type:
        select_type = 'Oracle数据库'.decode("utf-8")
    date_range = request.GET.get('date_range')
    if not date_range:
        date_range = '1天'.decode("utf-8")
    select_tags = request.GET.get('select_tags')
    if not select_tags:
        select_tags = '选择一个或多个'.decode("utf-8")
    select_form = request.GET.get('select_form')
    if not select_form:
        select_form = 'excel'
    file_tag = request.GET.get('file_tag')
    if not file_tag:
        file_tag = ''
    check_list = models_frame.CheckList.objects.all().order_by("-check_tag")

    check_err = models_frame.CheckInfo.objects.filter(check_tag=file_tag)
    begin_time = request.GET.get('begin_time')
    if not begin_time:
        begin_time = ''
    end_time = request.GET.get('end_time')
    if not end_time:
        end_time = ''

    # 当前时间
    now = tools.now()
    if request.method == 'POST':
        if request.POST.has_key('go_check'):
            select_type = request.POST.get('select_type', None)
            date_range = request.POST.get('date_range', None)
            select_tags = request.POST.getlist('select_tags', None)
            print ''.join(select_tags)
            select_form = request.POST.get('select_form', None)
            # begin_time = (datetime.datetime.now() - datetime.timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S")
            begin_time = tools.range(date_range)
            end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            file_tag = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            check_file_name  = 'oracheck_' + file_tag +  '.xls'
            sql = "insert into check_list(check_tag,check_type,server_tag,begin_time,end_time) values(%s,%s,%s,%s,%s)"
            value = (file_tag,'Oracle数据库',','.join(select_tags),begin_time,end_time)
            tools.mysql_exec(sql,value)
            easy_check.ora_check(select_tags,begin_time,end_time,check_file_name,file_tag)
            tags = ''
            for tag in select_tags:
                tags =  tag + ','
            return HttpResponseRedirect('/my_check?select_type=%s&date_range=%s&select_tags=%s&select_form=%s&file_tag=%s&begin_time=%s&end_time=%s' %(select_type,date_range,tags,select_form,file_tag,begin_time,end_time))

        else:
            logout(request)
            return HttpResponseRedirect('/login/')

    if messageinfo_list:
        msg_num = len(messageinfo_list)
        msg_last = models_frame.TabAlarmInfo.objects.latest('id')
        msg_last_content = msg_last.alarm_content
        tim_last = (datetime.datetime.now() - msg_last.alarm_time).seconds / 60
    else:
        msg_num = 0
        msg_last_content = ''
        tim_last = ''

    return render_to_response('frame/my_check.html', {'messageinfo_list': messageinfo_list, 'msg_num': msg_num, 'now': now,
                                                'msg_last_content': msg_last_content, 'tim_last': tim_last,
                                                'select_type': select_type, 'date_range': date_range,
                                                'select_tags': select_tags, 'select_form': select_form,'check_list':check_list,
                                                'file_tag': file_tag, 'check_err': check_err, 'begin_time': begin_time,
                                                      'end_time': end_time, 'linuxtagsinfo':linuxtagsinfo, 'oracletagsinfo':oracletagsinfo,
                                                      'mysqltagsinfo':mysqltagsinfo})

@login_required(login_url='/login')
def check_err(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()

    check_tag = request.GET.get('check_tag')

    check_err = models_frame.CheckInfo.objects.filter(check_tag=check_tag)


    # 当前时间
    now = tools.now()
    if request.method == 'POST':
        logout(request)
        return HttpResponseRedirect('/login/')

    if messageinfo_list:
        msg_num = len(messageinfo_list)
        msg_last = models_frame.TabAlarmInfo.objects.latest('id')
        msg_last_content = msg_last.alarm_content
        tim_last = (datetime.datetime.now() - msg_last.alarm_time).seconds / 60
    else:
        msg_num = 0
        msg_last_content = ''
        tim_last = ''

    return render_to_response('frame/check_err.html', {'messageinfo_list': messageinfo_list, 'msg_num': msg_num, 'now': now,
                                                'msg_last_content': msg_last_content, 'tim_last': tim_last, 'check_err': check_err})

@login_required(login_url='/login')
def checklist_del(request):
    check_tag = request.GET.get('check_tag')
    models_frame.CheckList.objects.filter(check_tag=check_tag).delete()
    return HttpResponseRedirect('/my_check/')

def page_not_found(request):
    return render(request, '404.html')

def page_inter_error(request):
    return render(request, '500.html')

def download(request):
    select_form = request.GET.get('select_form')
    file_tag = request.GET.get('file_tag')
    file_path = os.path.dirname(os.getcwd()) + '/dbmon/check_result/'
    if select_form == 'excel':
        if not file_tag:
            file = file_path + 'oracheck.xls'
            file_name = 'oracheck.xls'
        else:
            file = file_path + 'oracheck_' + file_tag + '.xls'
            file_name = 'oracheck_' + file_tag + '.xls'
    elif select_form == 'txt':
        if not file_tag:
            file = file_path + 'oracheck.txt'
            file_name = 'oracheck.txt'
        else:
            file = file_path + 'oracheck_' + file_tag + '.txt'
            file_name = 'oracheck_' + file_tag + '.txt'

    file=open(file,'rb')
    response =FileResponse(file)
    response['Content-Type']='application/octet-stream'
    response['Content-Disposition']='attachment;filename=%s' %file_name
    return response

@login_required(login_url='/login')
def my_tools(request):
    # 告警
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()

    now = tools.now()
    if request.method == 'POST':
        logout(request)
        return HttpResponseRedirect('/login/')
    if messageinfo_list:
        msg_num = len(messageinfo_list)
        msg_last = models_frame.TabAlarmInfo.objects.latest('id')
        msg_last_content = msg_last.alarm_content
        tim_last = (datetime.datetime.now() - msg_last.alarm_time).seconds / 60
        return render_to_response('frame/my_tools.html', {'messageinfo_list': messageinfo_list,
                                                   'msg_num': msg_num,'now':now,
                                                   'msg_last_content': msg_last_content, 'tim_last': tim_last})
    else:
        msg_num = 0
        msg_last_content = ''
        tim_last = ''
        return render_to_response('frame/my_tools.html',
                                  {'messageinfo_list': messageinfo_list, 'now': now,
                                   'msg_last_content': msg_last_content, 'tim_last': tim_last})

@login_required(login_url='/login')
def log_collect(request):
    # 告警
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    # 日志采集列表
    log_collect_list = models_frame.LogCollectConf.objects.all()
    paginator_log = Paginator(log_collect_list, 5)
    page_log = request.GET.get('page_log')
    try:
        log_collects = paginator_log.page(page_log)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        log_collects = paginator_log.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        log_collects = paginator_log.page(paginator_log.num_pages)
    now = tools.now()
    if request.method == 'POST':
        if request.POST.has_key('go_collect'):
            log_type = '日志采集'
            local_dir = request.POST.get('local_dir', None)
            collect.go_collect(local_dir)
            messages.add_message(request,messages.INFO,'正在收集')
            return HttpResponseRedirect('/log_info?log_type=%s' %log_type)

        else:
            logout(request)
            return HttpResponseRedirect('/login/')
    if messageinfo_list:
        msg_num = len(messageinfo_list)
        msg_last = models_frame.TabAlarmInfo.objects.latest('id')
        msg_last_content = msg_last.alarm_content
        tim_last = (datetime.datetime.now() - msg_last.alarm_time).seconds / 60
    else:
        msg_num = 0
        msg_last_content = ''
        tim_last = ''
    return render(request, 'frame/log_collect.html', {'messageinfo_list': messageinfo_list, 'log_collects': log_collects,
                                                   'msg_num': msg_num, 'now': now,
                                                   'msg_last_content': msg_last_content, 'tim_last': tim_last})

@login_required(login_url='/login')
def log_collects_edit(request):
    status = 0
    rid = request.GET.get('id')
    log_collect_edit = models_frame.LogCollectConf.objects.get(id=rid)
    if request.method == "POST":
        if request.POST.has_key('commit'):
            app_name = request.POST.get('app_name', None)
            host = request.POST.get('host', None)
            user = request.POST.get('user', None)
            password = base64.encodestring(request.POST.get('password', None))
            log_name = request.POST.get('log_name', None)
            log_path = request.POST.get('log_path', None)
            models_frame.LogCollectConf.objects.filter(id=rid).update(app_name=app_name,host=host, user=user,
                                                                 password=password, log_name = log_name,
                                                                 log_path = log_path)
            status = 1
        elif request.POST.has_key('logout'):
            logout(request)
            return HttpResponseRedirect('/login/')


    return render_to_response('frame/log_collects_edit.html', {'log_collect_edit': log_collect_edit, 'status':status})

@login_required(login_url='/login')
def log_collects_add(request):
    status = 0
    if request.method == "POST":
        if request.POST.has_key('commit'):
            app_name = request.POST.get('app_name', None)
            host = request.POST.get('host', None)
            user = request.POST.get('user', None)
            password = base64.encodestring(request.POST.get('password', None))
            log_name = request.POST.get('log_name', None)
            log_path = request.POST.get('log_path', None)
            models_frame.LogCollectConf.objects.create(app_name=app_name,host=host, user=user, password=password,
                                                       log_name=log_name, log_path=log_path)
            status = 1
        elif request.POST.has_key('logout'):
            logout(request)
            return HttpResponseRedirect('/login/')

    return render_to_response('frame/log_collects_add.html', {'status':status})

@login_required(login_url='/login')
def log_collects_del(request):
    rid = request.GET.get('id')
    models_frame.LogCollectConf.objects.filter(id=rid).delete()
    return HttpResponseRedirect('/log_collect/')

@login_required(login_url='/login')
def easy_start(request):
    # 告警
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()

    # 程序启停列表
    easy_start_list = models_frame.EasyStartConf.objects.all()
    paginator_start = Paginator(easy_start_list, 5)
    page_start = request.GET.get('page_start')
    try:
        easy_starts = paginator_start.page(page_start)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        easy_starts = paginator_start.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        easy_starts = paginator_start.page(paginator_start.num_pages)
    now = tools.now()
    if request.method == 'POST':
        if request.POST.has_key('go_start'):
            log_type = '程序启停'
            start.go_start()
            return HttpResponseRedirect('/log_info?log_type=%s' % log_type)
        elif request.POST.has_key('reset'):
            upd_1_sql = "update easy_start_conf set process_check_result=''"
            upd_2_sql = "update easy_start_conf set check_log_result=''"
            tools.mysql_exec(upd_1_sql,'')
            tools.mysql_exec(upd_2_sql,'')
            return HttpResponseRedirect('/easy_start/')

        else:
            logout(request)
            return HttpResponseRedirect('/login/')
    if messageinfo_list:
        msg_num = len(messageinfo_list)
        msg_last = models_frame.TabAlarmInfo.objects.latest('id')
        msg_last_content = msg_last.alarm_content
        tim_last = (datetime.datetime.now() - msg_last.alarm_time).seconds / 60
        return render_to_response('frame/easy_start.html', {'messageinfo_list': messageinfo_list, 'easy_starts':easy_starts,
                                                   'msg_num': msg_num,'now':now,
                                                   'msg_last_content': msg_last_content, 'tim_last': tim_last})
    else:
        msg_num = 0
        msg_last_content = ''
        tim_last = ''
        return render_to_response('frame/easy_start.html',
                                  {'messageinfo_list': messageinfo_list, 'easy_starts':easy_starts,'now': now,
                                   'msg_last_content': msg_last_content, 'tim_last': tim_last})

@login_required(login_url='/login')
def easy_starts_edit(request):
    status = 0
    rid = request.GET.get('id')
    easy_start_edit = models_frame.EasyStartConf.objects.get(id=rid)
    if request.method == "POST":
        if request.POST.has_key('commit'):
            oper_type = request.POST.get('oper_type', None)
            app_name = request.POST.get('app_name', None)
            host = request.POST.get('host', None)
            user = request.POST.get('user', None)
            password = base64.encodestring(request.POST.get('password', None))
            name = request.POST.get('name', None)
            do_cmd = request.POST.get('do_cmd', None)
            process_check = request.POST.get('process_check', None)
            check_log = request.POST.get('check_log', None)
            models_frame.EasyStartConf.objects.filter(id=rid).update(oper_type=oper_type,app_name=app_name,host=host, user=user,
                                                                 password=password,name=name, do_cmd = do_cmd,process_check = process_check,
                                                                     check_log = check_log)
            status = 1
        elif request.POST.has_key('logout'):
            logout(request)
            return HttpResponseRedirect('/login/')

    return render_to_response('frame/easy_starts_edit.html', {'easy_start_edit': easy_start_edit, 'status':status})

@login_required(login_url='/login')
def easy_starts_add(request):
    status = 0
    if request.method == "POST":
        if request.POST.has_key('commit'):
            oper_type = request.POST.get('oper_type', None)
            app_name = request.POST.get('app_name', None)
            host = request.POST.get('host', None)
            user = request.POST.get('user', None)
            password = base64.encodestring(request.POST.get('password', None))
            name = request.POST.get('name', None)
            do_cmd = request.POST.get('do_cmd', None)
            process_check = request.POST.get('process_check', None)
            check_log = request.POST.get('check_log', None)
            models_frame.EasyStartConf.objects.create(oper_type=oper_type,app_name=app_name,host=host, user=user,
                                                                 password=password, do_cmd = do_cmd, name = name,process_check = process_check,
                                                                     check_log = check_log)
            status = 1
        elif request.POST.has_key('logout'):
            logout(request)
            return HttpResponseRedirect('/login/')

    return render_to_response('frame/easy_starts_add.html', {'status':status})

@login_required(login_url='/login')
def easy_starts_del(request):
    rid = request.GET.get('id')
    models_frame.EasyStartConf.objects.filter(id=rid).delete()
    return HttpResponseRedirect('/easy_start/')


@login_required(login_url='/login')
def log_info(request):
    # 告警
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    log_type = request.GET.get('log_type')

    # 日志采集列表
    log_info = models_frame.ManyLogs.objects.filter(log_type=log_type)

    now = tools.now()

    if request.method == 'POST':
        logout(request)
        return HttpResponseRedirect('/login/')

    if messageinfo_list:
        msg_num = len(messageinfo_list)
        msg_last = models_frame.TabAlarmInfo.objects.latest('id')
        msg_last_content = msg_last.alarm_content
        tim_last = (datetime.datetime.now() - msg_last.alarm_time).seconds / 60
    else:
        msg_num = 0
        msg_last_content = ''
        tim_last = ''
        return render_to_response('frame/log_info.html', {'messageinfo_list': messageinfo_list, 'log_info':log_info,
                                                   'msg_num': msg_num,'now':now,
                                                   'msg_last_content': msg_last_content, 'tim_last': tim_last})



@login_required(login_url='/login')
def oracle_install(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    if request.method == "POST":
        if request.POST.has_key('commit'):
            host_name = request.POST.get('host_name', None)
            host = request.POST.get('host', None)
            password = request.POST.get('password', None)
            linux_version = request.POST.get('linux_version', None)
            oracle_version = request.POST.get('oracle_version', None)
            soft_dir = request.POST.get('soft_dir', None)
            data_dir = request.POST.get('data_dir', None)

            task.oracle_install.delay(host,'root',password)
            log_type = 'Oracle部署'
            return HttpResponseRedirect('/log_info?log_type=%s' % log_type)

        elif request.POST.has_key('logout'):
            logout(request)
            return HttpResponseRedirect('/login/')

    if messageinfo_list:
        msg_num = len(messageinfo_list)
        msg_last = models_frame.TabAlarmInfo.objects.latest('id')
        msg_last_content = msg_last.alarm_content
        tim_last = (datetime.datetime.now() - msg_last.alarm_time).seconds / 60
        return render_to_response('oracle_mon/oracle_install.html',
                                  {'messageinfo_list': messageinfo_list, 'msg_num': msg_num,
                                   'msg_last_content': msg_last_content, 'tim_last': tim_last})
    else:
        return render_to_response('oracle_mon/oracle_install.html', )

@login_required(login_url='/login')
def mysql_install(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    if request.method == "POST":
        if request.POST.has_key('commit'):
            host_name = request.POST.get('host_name', None)
            host = request.POST.get('host', None)
            password = request.POST.get('password', None)
            linux_version = request.POST.get('linux_version', None)
            ssh_port = request.POST.get('ssh_port', None)
            mysql_version = request.POST.get('oracle_version', None)
            mysql_base = request.POST.get('mysql_base', None)
            data_path = request.POST.get('data_path', None)
            port = request.POST.get('port', None)
            task.mysql_install.delay(host,'root',password,ssh_port,data_path,mysql_base,port)
            log_type = 'MySQL部署'
            return HttpResponseRedirect('/log_info?log_type=%s' % log_type)

        elif request.POST.has_key('logout'):
            logout(request)
            return HttpResponseRedirect('/login/')

    if messageinfo_list:
        msg_num = len(messageinfo_list)
        msg_last = models_frame.TabAlarmInfo.objects.latest('id')
        msg_last_content = msg_last.alarm_content
        tim_last = (datetime.datetime.now() - msg_last.alarm_time).seconds / 60
        return render_to_response('mysql_mon/mysql_install.html',
                                  {'messageinfo_list': messageinfo_list, 'msg_num': msg_num,
                                   'msg_last_content': msg_last_content, 'tim_last': tim_last})
    else:
        return render_to_response('mysql_mon/mysql_install.html', )


def my_task(request):
    # 告警
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()

    # 数据库操作面板
    my_task_sql = '''select t1.id,t1.task_id,
               t1.task_name,
               t1.server_type,
               t1.tags,
               t1.oper_type,
               t1.args,
               t1.result,
               t1.start_time,
               t1.end_time,
               t1.runtime,
               t1.state,
               (case t1.state
               when 'RUNNING' then 'default' 
               when 'SUCCESS' then 'success' 
               else 'danger' end) state_color
          from my_task t1 order by id desc '''

    my_task_list = tools.mysql_django_query(my_task_sql)

    now = tools.now()
    if request.method == 'POST':
        logout(request)
        return HttpResponseRedirect('/login/')

    if messageinfo_list:
        msg_num = len(messageinfo_list)
        msg_last = models_frame.TabAlarmInfo.objects.latest('id')
        msg_last_content = msg_last.alarm_content
        tim_last = (datetime.datetime.now() - msg_last.alarm_time).seconds / 60
    else:
        msg_num = 0
        msg_last_content = ''
        tim_last = ''
    return render(request, 'frame/my_task.html',
                  {'messageinfo_list': messageinfo_list, 'my_task_list': my_task_list,
                               'msg_num': msg_num, 'now': now,
                               'msg_last_content': msg_last_content, 'tim_last': tim_last}
                  )


@login_required(login_url='/login')
def show_sqltext_mysql(request):
    id = request.GET.get('id')
    sql = "select sql_text from mysql_slowquery where id =%d " %int(id)
    sqltext = tools.mysql_django_query(sql)


    return render_to_response('mysql_mon/show_sqltext_mysql.html', {'sqltext':sqltext})



@login_required(login_url='/login')
def my_scheduler(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()

    # 查询定时任务
    sql = "select a.id,a.name,a.task,a.kwargs,a.expires,JSON_UNQUOTE(JSON_EXTRACT(a.kwargs,'$.tags')) tags,JSON_UNQUOTE(JSON_EXTRACT(a.description,'$.type')) type,JSON_UNQUOTE(JSON_EXTRACT(a.description,'$.task_model')) task_model," \
          "a.enabled,(case a.enabled when 1 then 'on' else 'off' end) is_on," \
          "(case a.enabled when 1 then 'green' else 'red' end) is_on1,a.last_run_at,a.total_run_count,a.date_changed," \
          "a.description,concat(b.minute,' ',b.hour,' ',b.day_of_week,' ',b.day_of_month,' ',b.day_of_month) crontab,a.interval_id from djcelery_periodictask a left join djcelery_crontabschedule b on " \
          "a.crontab_id=b.id where a.name <> 'celery.backend_cleanup' order by id"

    my_schedulers = tools.mysql_django_query(sql)

    # 查询crontab
    sql = "select id,concat(b.minute,' ',b.hour,' ',b.day_of_week,' ',b.day_of_month,' ',b.day_of_month) crontab from djcelery_crontabschedule b "

    my_crontabs = tools.mysql_django_query(sql)


    if request.method == 'POST':
        logout(request)
        return HttpResponseRedirect('/login/')

    if messageinfo_list:
        msg_num = len(messageinfo_list)
        msg_last = models_frame.TabAlarmInfo.objects.latest('id')
        msg_last_content = msg_last.alarm_content
        tim_last = (datetime.datetime.now() - msg_last.alarm_time).seconds / 60
    else:
        msg_num = 0
        msg_last_content = ''
        tim_last = ''
    return render_to_response('frame/my_scheduler.html',
                              {'messageinfo_list': messageinfo_list, 'msg_num': msg_num,
                               'msg_last_content': msg_last_content, 'tim_last': tim_last,
                               'my_schedulers':my_schedulers,'my_crontabs':my_crontabs})

@login_required(login_url='/login')
def scheduler_add(request):
    linuxtagsinfo = models_linux.TabLinuxServers.objects.all().order_by('tags')
    oracletagsinfo = models_oracle.TabOracleServers.objects.all().order_by('tags')
    mysqltagsinfo = models_mysql.TabMysqlServers.objects.all().order_by('tags')

    status = 0
    sql = "select id,concat(b.minute,' ',b.hour,' ',b.day_of_week,' ',b.day_of_month,' ',b.day_of_month) crontab from djcelery_crontabschedule b"
    my_crontabs = tools.mysql_django_query(sql)


    if request.method == "POST":
        if request.POST.has_key('commit'):
            task_name = request.POST.get('task_name', None)
            type = request.POST.get('type', None)
            tags = request.POST.get('tags', None)
            task_model = request.POST.get('task_model', None)
            task = tools.task_model(task_model)
            is_on = request.POST.get('is_on', None)
            is_on = tools.isno(is_on)
            crontab = request.POST.get('crontab', None)
            para_name = request.POST.getlist('para_name', None)
            para_value = request.POST.getlist('para_value', None)
            # 描述信息
            des_d = {}
            des_d['type'] = type
            des_d['task_model'] = task_model
            des = json.dumps(des_d, ensure_ascii=False)

            kwargs_d = {}
            user = ''
            password = ''
            service_name = ''
            url = ''

            if type == unicode('Oracle数据库', 'utf-8'):
                # 获取oracle用户名密码等信息
                sql = "select host,port,service_name_cdb,user,password,user_os,password_os,ssh_port_os from tab_oracle_servers where tags= '%s' " % tags
                oracle = tools.mysql_query(sql)
                host = oracle[0][0]
                port = oracle[0][1]
                service_name = oracle[0][2]
                user = oracle[0][3]
                password = oracle[0][4]
                password = base64.decodestring(password)
                user_os = oracle[0][5]
                password_os = oracle[0][6]
                password_os = base64.decodestring(password_os)
                ssh_port_os = oracle[0][7]
                url = host + ':' + port + '/' + service_name
            elif type == unicode('MySQL数据库', 'utf-8'):
                sql = "select host,user,password,user_os,password_os,ssh_port_os from tab_mysql_servers where tags= '%s' " % tags
                mysql = tools.mysql_query(sql)
                host = mysql[0][0]
                user = mysql[0][1]
                password = mysql[0][2]
                password = base64.decodestring(password)
                user_os = mysql[0][3]
                password_os = mysql[0][4]
                password_os = base64.decodestring(password_os)
                ssh_port_os = mysql[0][5]
            else:
                sql = "select host,user,password,ssh_port from tab_linux_servers where tags= '%s' " % tags
                linux = tools.mysql_query(sql)
                host = linux[0][0]
                user_os = linux[0][1]
                password_os = linux[0][2]
                password_os = base64.decodestring(password_os)
                ssh_port_os = linux[0][3]

            # 通用参数
            kwargs_d['tags'] = tags
            kwargs_d['host'] = host
            if user:
                kwargs_d['user'] = user
            if password:
                kwargs_d['password'] = password
            kwargs_d['user_os'] = user_os
            kwargs_d['password_os'] = password_os
            if service_name:
                kwargs_d['service_name'] = service_name
            if url:
                kwargs_d['url'] = url
            kwargs_d['ssh_port_os'] = ssh_port_os

            # 自定义参数
            if para_name:
                for i in xrange(len(para_name)):
                    para = para_name[i]
                    value = para_value[i]
                    if para:
                        kwargs_d[para] = value
            # 将参数转化为json格式
            kwargs = json.dumps(kwargs_d)

            sql = "insert into djcelery_periodictask(name,task,args,kwargs,expires,enabled,crontab_id,description,total_run_count,date_changed) values(%s,%s,'[]',%s,null,%s,%s,%s,0,now())"
            value = (task_name, task, kwargs, is_on, crontab, des)
            tools.mysql_exec(sql,value)
            status = 1


        elif request.POST.has_key('logout'):
            logout(request)
            return HttpResponseRedirect('/login/')

    return render_to_response('frame/scheduler_add.html', {'status':status, 'my_crontabs':my_crontabs, 'linuxtagsinfo':linuxtagsinfo, 'oracletagsinfo':oracletagsinfo,
                                                     'mysqltagsinfo':mysqltagsinfo})

@login_required(login_url='/login')
def scheduler_del(request):
    rid = request.GET.get('id')
    sql = "delete from djcelery_periodictask where id = %s " %rid
    tools.mysql_exec(sql,'')
    return HttpResponseRedirect('/my_scheduler/')

@login_required(login_url='/login')
def scheduler_edit(request):
    rid = request.GET.get('id')
    linuxtagsinfo = models_linux.TabLinuxServers.objects.all().order_by('tags')
    oracletagsinfo = models_oracle.TabOracleServers.objects.all().order_by('tags')
    mysqltagsinfo = models_mysql.TabMysqlServers.objects.all().order_by('tags')

    status = 0

    # 查询定时任务
    sql = "select a.id,a.name,a.task,a.kwargs,a.expires," \
          "a.enabled,(case a.enabled when 1 then '启用' else '禁用' end) is_on," \
          "(case a.enabled when 1 then 'green' else 'red' end) is_on1,a.last_run_at,a.total_run_count,a.date_changed," \
          "a.description,a.crontab_id,concat(b.minute,' ',b.hour,' ',b.day_of_week,' ',b.day_of_month,' ',b.day_of_month) crontab,a.interval_id from djcelery_periodictask a left join djcelery_crontabschedule b on " \
          "a.crontab_id=b.id where a.id=%s " %rid

    my_scheduler = tools.mysql_django_query(sql)

    # 查询crontab
    sql = "select id,concat(b.minute,' ',b.hour,' ',b.day_of_week,' ',b.day_of_month,' ',b.day_of_month) crontab from djcelery_crontabschedule b"
    my_crontabs = tools.mysql_django_query(sql)

    # 查询变量信息，description
    sql = "select kwargs,description from djcelery_periodictask where id = %s" %rid
    res = tools.mysql_query(sql)

    twargs_j = str(res[0][0])
    twargs_d = json.loads(twargs_j,encoding='utf-8')
    tags = twargs_d['tags']

    # 删除tags,user,password,url等通用参数
    if 'tags' in twargs_d:
        twargs_d.pop('tags')
    twargs_d.pop('host')
    if 'user' in twargs_d:
        twargs_d.pop('user')
    if 'password' in twargs_d:
        twargs_d.pop('password')
    twargs_d.pop('user_os')
    twargs_d.pop('password_os')
    twargs_d.pop('ssh_port_os')
    if 'service_name' in twargs_d:
        twargs_d.pop('service_name')
    if 'url' in twargs_d:
        twargs_d.pop('url')

    description_j = str(res[0][1])
    description_d = json.loads(description_j,encoding='utf-8')
    type = description_d['type']
    task_model = description_d['task_model']


    if request.method == "POST":
        if request.POST.has_key('commit'):
            task_name = request.POST.get('task_name', None)
            type = request.POST.get('type', None)
            tags = request.POST.get('tags', None)
            task_model = request.POST.get('task_model', None)
            task = tools.task_model(task_model)
            is_on = request.POST.get('is_on', None)
            is_on = tools.isno(is_on)
            crontab = request.POST.get('crontab', None)
            para_name = request.POST.getlist('para_name', None)
            para_value = request.POST.getlist('para_value', None)

            des_d = {}
            des_d['type'] = type
            des_d['task_model'] = task_model
            des = json.dumps(des_d, ensure_ascii=False)

            kwargs_d = {}
            user = ''
            password = ''
            service_name = ''
            url = ''

            if type == unicode('Oracle数据库', 'utf-8'):
                # 获取oracle用户名密码等信息
                sql = "select host,port,service_name_cdb,user,password,user_os,password_os,ssh_port_os from tab_oracle_servers where tags= '%s' " % tags
                oracle = tools.mysql_query(sql)
                host = oracle[0][0]
                port = oracle[0][1]
                service_name = oracle[0][2]
                user = oracle[0][3]
                password = oracle[0][4]
                password = base64.decodestring(password)
                user_os = oracle[0][5]
                password_os = oracle[0][6]
                password_os = base64.decodestring(password_os)
                ssh_port_os = oracle[0][7]
                url = host + ':' + port + '/' + service_name
            elif type == unicode('MySQL数据库', 'utf-8'):
                sql = "select host,user,password,user_os,password_os,ssh_port_os from tab_mysql_servers where tags= '%s' " % tags
                mysql = tools.mysql_query(sql)
                host = mysql[0][0]
                user = mysql[0][1]
                password = mysql[0][2]
                password = base64.decodestring(password)
                user_os = mysql[0][3]
                password_os = mysql[0][4]
                password_os = base64.decodestring(password_os)
                ssh_port_os = mysql[0][5]
            else:
                sql = "select host,user,password,ssh_port from tab_linux_servers where tags= '%s' " % tags
                linux = tools.mysql_query(sql)
                host = linux[0][0]
                user_os = linux[0][1]
                password_os = linux[0][2]
                password_os = base64.decodestring(password_os)
                ssh_port_os = linux[0][3]

            # 通用参数
            kwargs_d['tags'] = tags
            kwargs_d['host'] = host

            if user:
                kwargs_d['user'] = user
            if password:
                kwargs_d['password'] = password
            kwargs_d['user_os'] = user_os
            kwargs_d['password_os'] = password_os
            kwargs_d['ssh_port_os'] = ssh_port_os
            if service_name:
                kwargs_d['service_name'] = service_name
            if url:
                kwargs_d['url'] = url

            # 自定义参数
            if para_name:
                for i in xrange(len(para_name)):
                    para = para_name[i]
                    value = para_value[i]
                    if para:
                        kwargs_d[para] = value


            kwargs = json.dumps(kwargs_d)

            sql = "delete from djcelery_periodictask where id = %s " %rid

            tools.mysql_exec(sql,'')

            sql = "insert into djcelery_periodictask(name,task,args,kwargs,expires,enabled,crontab_id,description,total_run_count,date_changed) values(%s,%s,'[]',%s,null,%s,%s,%s,0,now())"
            value = (task_name, task, kwargs, is_on, crontab, des)
            tools.mysql_exec(sql, value)
            status = 1

        elif request.POST.has_key('logout'):
            logout(request)
            return HttpResponseRedirect('/login/')

    return render_to_response('frame/scheduler_edit.html', {'status':status, 'my_scheduler':my_scheduler, 'linuxtagsinfo':linuxtagsinfo, 'oracletagsinfo':oracletagsinfo,
                                                     'mysqltagsinfo':mysqltagsinfo,'type':type,'task_model':task_model,'tags':tags,'my_crontabs':my_crontabs,
                                                      'twargs_d':twargs_d})


@login_required(login_url='/login')
def scheduler_para(request):
    rid = request.GET.get('id')

    # 查询变量信息，description
    sql = "select kwargs from djcelery_periodictask where id = %s" %rid
    res = tools.mysql_query(sql)

    twargs_j = str(res[0][0])
    twargs_d = json.loads(twargs_j,encoding='utf-8')


    # 删除tags,user,password,url等通用参数
    if 'tags' in twargs_d:
        twargs_d.pop('tags')
    twargs_d.pop('host')
    if 'user' in twargs_d:
        twargs_d.pop('user')
    if 'password' in twargs_d:
        twargs_d.pop('password')
    twargs_d.pop('user_os')
    twargs_d.pop('password_os')
    twargs_d.pop('ssh_port_os')
    if 'service_name' in twargs_d:
        twargs_d.pop('service_name')
    if 'url' in twargs_d:
        twargs_d.pop('url')


    return render_to_response('frame/scheduler_para.html', {'twargs_d':twargs_d})


@login_required(login_url='/login')
def crontab_del(request):
    rid = request.GET.get('id')
    sql = "delete from djcelery_crontabschedule where id = %s " %rid
    tools.mysql_exec(sql,'')
    return HttpResponseRedirect('/my_scheduler/')


@login_required(login_url='/login')
def crontab_add(request):

    status = 0

    if request.method == "POST":
        if request.POST.has_key('commit'):
            minute = request.POST.get('minute', None)
            hour = request.POST.get('hour', None)
            dw = request.POST.get('dw', None)
            dm = request.POST.get('dm', None)
            my = request.POST.get('my', None)

            sql = "insert into djcelery_crontabschedule(minute,hour,day_of_week,day_of_month,month_of_year) values(%s,%s,%s,%s,%s)"
            value = (minute, hour, dw, dm, my)
            tools.mysql_exec(sql,value)
            status = 1


        elif request.POST.has_key('logout'):
            logout(request)
            return HttpResponseRedirect('/login/')

    return render_to_response('frame/crontab_add.html', {'status':status})

@login_required(login_url='/login')
def crontab_edit(request):
    rid = request.GET.get('id')
    status = 0
    # 查询crontab
    sql = "select id,minute,hour,day_of_week dw,day_of_month dm,month_of_year my from djcelery_crontabschedule b where id=%s" %rid
    my_crontabs = tools.mysql_django_query(sql)


    if request.method == "POST":
        if request.POST.has_key('commit'):
            minute = request.POST.get('minute', None)
            hour = request.POST.get('hour', None)
            dw = request.POST.get('dw', None)
            dm = request.POST.get('dm', None)
            my = request.POST.get('my', None)

            sql = "update djcelery_crontabschedule set minute='%s',hour='%s',day_of_week='%s',day_of_month='%s',month_of_year='%s' where id=%s " %(minute,hour,dw,dm,my,rid)

            tools.mysql_exec(sql, '')
            status = 1

        elif request.POST.has_key('logout'):
            logout(request)
            return HttpResponseRedirect('/login/')

    return render_to_response('frame/crontab_edit.html', {'status':status, 'my_crontabs':my_crontabs})

@login_required(login_url='/login')
def failure_add(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()

    if request.method == "POST":
        if request.POST.has_key('commit'):
            title = request.POST.get('title', None)
            level = request.POST.get('level', None)
            type = request.POST.get('type', None)
            related = request.POST.get('related', None)
            status = request.POST.get('status', None)
            start_time = request.POST.get('startTime', None)
            start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
            end_time = request.POST.get('endTime', None)
            end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
            person = request.POST.get('person', None)
            effect = request.POST.get('effect', None)
            analyze = request.POST.get('analyze', None)
            reason = request.POST.get('reason', None)
            solution = request.POST.get('solution', None)

            models_frame.FailureList.objects.create(title=title, level=level,type=type,related=related,status=status,
                                                    start_time=start_time,end_time=end_time,person=person,effect=effect,
                                                    analyze=analyze,reason=reason,solution=solution)

        elif request.POST.has_key('logout'):
            logout(request)
            return HttpResponseRedirect('/login/')

    if messageinfo_list:
        msg_num = len(messageinfo_list)
        msg_last = models_frame.TabAlarmInfo.objects.latest('id')
        msg_last_content = msg_last.alarm_content
        tim_last = (datetime.datetime.now() - msg_last.alarm_time).seconds / 60
    else:
        msg_num = 0
        msg_last_content = ''
        tim_last = ''

    return render_to_response('frame/failure_add.html',
                              {'messageinfo_list': messageinfo_list, 'msg_num': msg_num,
                               'msg_last_content': msg_last_content, 'tim_last': tim_last})



@login_required(login_url='/login')
def show_failure(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()

    failure_list = models_frame.FailureList.objects.all().order_by("-start_time")

    if request.method == 'POST':
        logout(request)
        return HttpResponseRedirect('/login/')

    if messageinfo_list:
        msg_num = len(messageinfo_list)
        msg_last = models_frame.TabAlarmInfo.objects.latest('id')
        msg_last_content = msg_last.alarm_content
        tim_last = (datetime.datetime.now() - msg_last.alarm_time).seconds / 60
    else:
        msg_num = 0
        msg_last_content = ''
        tim_last = ''
    return render_to_response('frame/show_failure.html',
                              {'messageinfo_list': messageinfo_list, 'msg_num': msg_num,
                               'msg_last_content': msg_last_content, 'tim_last': tim_last,
                               'failure_list':failure_list})


@login_required(login_url='/login')
def failure_del(request):
    rid = request.GET.get('id')
    sql = "delete from failure_list where id = %s " %rid
    tools.mysql_exec(sql,'')
    return HttpResponseRedirect('/show_failure/')

@login_required(login_url='/login')
def failure_content(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()

    rid = request.GET.get('id')

    faliure = models_frame.FailureList.objects.get(id=rid)

    if messageinfo_list:
        msg_num = len(messageinfo_list)
        msg_last = models_frame.TabAlarmInfo.objects.latest('id')
        msg_last_content = msg_last.alarm_content
        tim_last = (datetime.datetime.now() - msg_last.alarm_time).seconds / 60
    else:
        msg_num = 0
        msg_last_content = ''
        tim_last = ''

    return render_to_response('frame/failure_content.html',
                              {'messageinfo_list': messageinfo_list, 'msg_num': msg_num,
                               'msg_last_content': msg_last_content, 'tim_last': tim_last,
                               'faliure':faliure})

@login_required(login_url='/login')
def failure_edit(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    status = 0
    rid = request.GET.get('id')
    failure_edit = models_frame.FailureList.objects.get(id=rid)
    if request.method == "POST":
        if request.POST.has_key('commit'):
            title = request.POST.get('title', None)
            level = request.POST.get('level', None)
            type = request.POST.get('type', None)
            related = request.POST.get('related', None)
            status = request.POST.get('status', None)
            start_time = request.POST.get('startTime', None)
            start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
            end_time = request.POST.get('endTime', None)
            end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
            person = request.POST.get('person', None)
            effect = request.POST.get('effect', None)
            analyze = request.POST.get('analyze', None)
            reason = request.POST.get('reason', None)
            solution = request.POST.get('solution', None)

            models_frame.FailureList.objects.filter(id=rid).update(title=title, level=level,type=type,related=related,status=status,
                                                    start_time=start_time,end_time=end_time,person=person,effect=effect,
                                                    analyze=analyze,reason=reason,solution=solution)
            status = 1
            return HttpResponseRedirect('/show_failure/')
        elif request.POST.has_key('logout'):
            logout(request)
            return HttpResponseRedirect('/login/')

    if messageinfo_list:
        msg_num = len(messageinfo_list)
        msg_last = models_frame.TabAlarmInfo.objects.latest('id')
        msg_last_content = msg_last.alarm_content
        tim_last = (datetime.datetime.now() - msg_last.alarm_time).seconds / 60
    else:
        msg_num = 0
        msg_last_content = ''
        tim_last = ''


    return render_to_response('frame/failure_edit.html', {'messageinfo_list': messageinfo_list, 'msg_num': msg_num,
                               'msg_last_content': msg_last_content, 'tim_last': tim_last,
                                'failure_edit': failure_edit,'status':status})


def jqtest(request):
    return render_to_response('frame/test.html',)

@login_required(login_url='/login')
def my_scripts(request):
    # 告警
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()

    oracle_monitor_scripts = models_frame.MyScripts.objects.filter(server_type='Oracle').filter(script_type='Monitor')
    oracle_manage_scripts = models_frame.MyScripts.objects.filter(server_type='Oracle').filter(script_type='Manage')
    oracle_performance_scripts = models_frame.MyScripts.objects.filter(server_type='Oracle').filter(script_type='Performance')

    now = tools.now()
    if request.method == 'POST':
        logout(request)
        return HttpResponseRedirect('/login/')
    if messageinfo_list:
        msg_num = len(messageinfo_list)
        msg_last = models_frame.TabAlarmInfo.objects.latest('id')
        msg_last_content = msg_last.alarm_content
        tim_last = (datetime.datetime.now() - msg_last.alarm_time).seconds / 60
    else:
        msg_num = 0
        msg_last_content = ''
        tim_last = ''
    return render_to_response('frame/my_scripts.html', {'messageinfo_list': messageinfo_list,
                                                        'msg_num': msg_num, 'now': now,
                                                        'msg_last_content': msg_last_content,
                                                        'tim_last': tim_last, 'oracle_monitor_scripts': oracle_monitor_scripts,
                                                        'oracle_manage_scripts':oracle_manage_scripts,'oracle_performance_scripts':oracle_performance_scripts})


@login_required(login_url='/login')
def show_script_content(request):

    rid = request.GET.get('id')

    script = models_frame.MyScripts.objects.get(id=rid)

    return render_to_response('frame/show_script_content.html',
                              {'script':script})


def show_web_stats(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    web_url_list = models_frame.WebUrlStats.objects.order_by("res")

    if request.method == 'POST':
        logout(request)
        return HttpResponseRedirect('/login/')

    if messageinfo_list:
        msg_num = len(messageinfo_list)
        msg_last = models_frame.TabAlarmInfo.objects.latest('id')
        msg_last_content = msg_last.alarm_content
        tim_last = (datetime.datetime.now() - msg_last.alarm_time).seconds / 60
    else:
        msg_num = 0
        msg_last_content = ''
        tim_last = ''
    return render_to_response('frame/show_web_stats.html',
                              {'web_url_list': web_url_list, 'messageinfo_list': messageinfo_list, 'msg_num': msg_num,
                               'msg_last_content': msg_last_content, 'tim_last': tim_last})


def show_tcp_stats(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    tcp_list = models_frame.TcpStats.objects.order_by("res")

    if request.method == 'POST':
        logout(request)
        return HttpResponseRedirect('/login/')

    if messageinfo_list:
        msg_num = len(messageinfo_list)
        msg_last = models_frame.TabAlarmInfo.objects.latest('id')
        msg_last_content = msg_last.alarm_content
        tim_last = (datetime.datetime.now() - msg_last.alarm_time).seconds / 60
    else:
        msg_num = 0
        msg_last_content = ''
        tim_last = ''
    return render_to_response('frame/show_tcp_stats.html',
                              {'tcp_list': tcp_list, 'messageinfo_list': messageinfo_list, 'msg_num': msg_num,
                               'msg_last_content': msg_last_content, 'tim_last': tim_last})


