#! /usr/bin/python
# encoding:utf-8

import os
from django.shortcuts import render

from django.shortcuts import render,render_to_response,RequestContext
from django.http import HttpResponse, HttpResponseRedirect

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# Create your views here.
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from django.http import StreamingHttpResponse
from django.http import FileResponse

from django.contrib import messages

from django.http import HttpResponse
import datetime
from frame import tools
# 配置文件
import ConfigParser
import base64
import cx_Oracle
import paramiko
import frame.models as models_frame
import linux_mon.models as models_linux
import oracle_mon.models as models_oracle
import mysql_mon.models as models_mysql

import easy_check as easy_check
import log_collect as collect
import easy_start as start
import oracle_do as ora_do
import mysql_do as msql_do
import oracle_backupinfo
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
    return render_to_response('show_all.html',
                              {'messageinfo_list': messageinfo_list, 'linux_all_cnt': linux_all_cnt,
                               'linux_seccess_cnt': linux_seccess_cnt, 'linux_warning_cnt': linux_warning_cnt,
                               'linux_danger_cnt': linux_danger_cnt, 'ora_all_cnt': ora_all_cnt,
                               'ora_seccess_cnt': ora_seccess_cnt, 'ora_warning_cnt': ora_warning_cnt,
                               'ora_danger_cnt': ora_danger_cnt,
                               'msql_all_cnt': msql_all_cnt, 'msql_seccess_cnt': msql_seccess_cnt,
                               'msql_warning_cnt': msql_warning_cnt, 'msql_danger_cnt': msql_danger_cnt,
                               'msg_num': msg_num, 'top_5_cpu': top_5_cpu, 'top_5_mem': top_5_mem,'top_5_disk':top_5_disk, 'now': now,
                               'msg_last_content': msg_last_content, 'tim_last': tim_last})



@login_required(login_url='/login')
def mon_servers(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    # linux监控设备
    linux_servers_list = models_linux.TabLinuxServers.objects.all()
    paginator_linux = Paginator(linux_servers_list, 5)
    page_linux = request.GET.get('page_linux')
    try:
        linuxs_servers = paginator_linux.page(page_linux)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        linuxs_servers = paginator_linux.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        linuxs_servers = paginator_linux.page(paginator_linux.num_pages)
    # Oracle监控设备
    oracle_servers_list = models_oracle.TabOracleServers.objects.all()
    paginator_oracle = Paginator(oracle_servers_list, 5)
    page_oracle = request.GET.get('page_oracle')
    try:
        oracle_servers = paginator_oracle.page(page_oracle)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        oracle_servers = paginator_oracle.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        oracle_servers = paginator_oracle.page(paginator_oracle.num_pages)

    # Mysql监控设备
    mysql_servers_list = models_mysql.TabMysqlServers.objects.all()
    paginator_mysql = Paginator(mysql_servers_list, 5)
    page_mysql = request.GET.get('paginator_mysql')
    try:
        mysql_servers = paginator_mysql.page(page_mysql)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        mysql_servers = paginator_mysql.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        mysql_servers = paginator_mysql.page(paginator_mysql.num_pages)

    if request.method == 'POST':
        logout(request)
        return HttpResponseRedirect('/login/')

    if messageinfo_list:
        msg_num = len(messageinfo_list)
        msg_last = models_frame.TabAlarmInfo.objects.latest('id')
        msg_last_content = msg_last.alarm_content
        tim_last = (datetime.datetime.now() - msg_last.alarm_time).seconds / 60
        return render_to_response('mon_servers.html',
                                  {'linuxs_servers': linuxs_servers,'oracle_servers': oracle_servers,'mysql_servers': mysql_servers, 'messageinfo_list': messageinfo_list, 'msg_num': msg_num,
                                   'msg_last_content': msg_last_content, 'tim_last': tim_last})
    else:
        return render_to_response('mon_servers.html', {'linuxs_servers': linuxs_servers,'oracle_servers': oracle_servers,'mysql_servers': mysql_servers})

@login_required(login_url='/login')
def alarm_setting(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    # 告警策略
    alarm_list = models_frame.TabAlarmConf.objects.all().order_by('db_type')
    paginator_alarm = Paginator(alarm_list, 5)
    page_alarm = request.GET.get('page_alarm')
    try:
        alarm_settings = paginator_alarm.page(page_alarm)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        alarm_settings = paginator_alarm.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        alarm_settings = paginator_alarm.page(paginator_alarm.num_pages)

    if request.method == 'POST':
        logout(request)
        return HttpResponseRedirect('/login/')

    if messageinfo_list:
        msg_num = len(messageinfo_list)
        msg_last = models_frame.TabAlarmInfo.objects.latest('id')
        msg_last_content = msg_last.alarm_content
        tim_last = (datetime.datetime.now() - msg_last.alarm_time).seconds / 60
        return render_to_response('alarm_setting.html',
                                  {'alarm_settings': alarm_settings, 'messageinfo_list': messageinfo_list, 'msg_num': msg_num,
                                   'msg_last_content': msg_last_content, 'tim_last': tim_last})
    else:
        return render_to_response('alarm_setting.html', {'alarm_settings': alarm_settings})


@login_required(login_url='/login')
def alarm_settings_edit(request):
    status = 0
    rid = request.GET.get('id')
    alarm_setting_edit = models_frame.TabAlarmConf.objects.get(id=rid)
    if request.method == "POST":
        if request.POST.has_key('commit'):
            db_type = request.POST.get('db_type', None)
            alarm_name = request.POST.get('alarm_name', None)

            pct_max = request.POST.get('pct_max', None)
            size_min = request.POST.get('size_min', None)
            time_max = request.POST.get('time_max', None)
            num_max = request.POST.get('num_max', None)

            models_frame.TabAlarmConf.objects.filter(id=rid).update(pct_max = pct_max,
                                                              size_min = size_min, time_max = time_max,num_max = num_max)
            status = 1
        elif request.POST.has_key('logout'):
            logout(request)
            return HttpResponseRedirect('/login/')

    return render_to_response('alarm_settings_edit.html', {'alarm_setting_edit': alarm_setting_edit,'status':status})


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
            connect_cn = request.POST.get('connect', None)
            connect = tools.isno(connect_cn)
            cpu_cn = request.POST.get('cpu', None)
            cpu = tools.isno(cpu_cn)
            mem_cn = request.POST.get('mem', None)
            mem = tools.isno(mem_cn)
            disk_cn = request.POST.get('disk', None)
            disk = tools.isno(disk_cn)
            models_linux.TabLinuxServers.objects.filter(id=rid).update(tags=tags,host_name=host_name, host=host, user=user,
                                                                 password=password, connect_cn=connect_cn,
                                                                 connect=connect,
                                                                 cpu_cn=cpu_cn, cpu=cpu, mem_cn=mem_cn, mem=mem,
                                                                 disk_cn=disk_cn, disk=disk)
            status = 1
        elif request.POST.has_key('logout'):
            logout(request)
            return HttpResponseRedirect('/login/')

    return render_to_response('linux_servers_edit.html', {'linux_server_edit': linux_server_edit,'status':status})

@login_required(login_url='/login')
def linux_servers_add(request):
    status = 0
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    if request.method == "POST":
        if request.POST.has_key('commit'):
            tags = request.POST.get('tags', None)
            host_name = request.POST.get('host_name', None)
            host = request.POST.get('host', None)
            user = request.POST.get('user', None)
            password = base64.encodestring(request.POST.get('password', None))
            connect_cn = request.POST.get('connect', None)
            connect = tools.isno(connect_cn)
            cpu_cn = request.POST.get('cpu', None)
            cpu = tools.isno(cpu_cn)
            mem_cn = request.POST.get('mem', None)
            mem = tools.isno(mem_cn)
            disk_cn = request.POST.get('disk', None)
            disk = tools.isno(disk_cn)
            models_linux.TabLinuxServers.objects.create(tags=tags,host_name=host_name, host=host, user=user, password=password,
                                                  connect_cn=connect_cn, connect=connect,
                                                  cpu_cn=cpu_cn, cpu=cpu, mem_cn=mem_cn, mem=mem, disk_cn=disk_cn,
                                                  disk=disk)
            status = 1
        elif request.POST.has_key('logout'):
            logout(request)
            return HttpResponseRedirect('/login/')

    return render_to_response('linux_servers_add.html', {'status':status})

@login_required(login_url='/login')
def linux_servers_del(request):
    rid = request.GET.get('id')
    models_linux.TabLinuxServers.objects.filter(id=rid).delete()
    return HttpResponseRedirect('/mon_servers/')

@login_required(login_url='/login')
def oracle_servers_add(request):
    status = 0
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    if request.method == "POST":
        if request.POST.has_key('commit'):
            tags = request.POST.get('tags', None)
            host = request.POST.get('host', None)
            port = request.POST.get('port', None)
            service_name = request.POST.get('service_name', None)
            user = request.POST.get('user', None)
            password = base64.encodestring(request.POST.get('password', None))
            user_os = request.POST.get('user_os', None)
            password_os = base64.encodestring(request.POST.get('password_os', None))
            connect_cn = request.POST.get('connect', None)
            connect = tools.isno(connect_cn)
            tbs_cn = request.POST.get('tbs', None)
            tbs = tools.isno(tbs_cn)
            adg_cn = request.POST.get('adg', None)
            adg = tools.isno(adg_cn)
            temp_tbs_cn = request.POST.get('temp_tbs', None)
            temp_tbs = tools.isno(temp_tbs_cn)
            undo_tbs_cn = request.POST.get('undo_tbs', None)
            undo_tbs = tools.isno(undo_tbs_cn)
            conn_cn = request.POST.get('conn', None)
            conn = tools.isno(conn_cn)
            err_info_cn = request.POST.get('err_info', None)
            err_info = tools.isno(err_info_cn)
            invalid_index_cn = request.POST.get('invalid_index', None)
            invalid_index = tools.isno(invalid_index_cn)
            oracle_lock_cn = request.POST.get('oracle_lock', None)
            oracle_lock = tools.isno(oracle_lock_cn)
            oracle_pwd_cn = request.POST.get('oracle_pwd', None)
            oracle_pwd = tools.isno(oracle_pwd_cn)
            oracle_pga_cn = request.POST.get('oracle_pga', None)
            oracle_pga = tools.isno(oracle_pga_cn)
            oracle_archive_cn = request.POST.get('oracle_archive', None)
            oracle_archive = tools.isno(oracle_archive_cn)
            models_oracle.TabOracleServers.objects.create(tags=tags,host=host, port=port, service_name=service_name,
                                                   user=user, password=password,
                                                   user_os=user_os, password_os=password_os, connect=connect,
                                                   connect_cn=connect_cn, tbs=tbs, tbs_cn=tbs_cn,
                                                   adg=adg, adg_cn=adg_cn, temp_tbs=temp_tbs, temp_tbs_cn=temp_tbs_cn,
                                                   undo_tbs=undo_tbs, undo_tbs_cn=undo_tbs_cn,
                                                   conn=conn, conn_cn=conn_cn, err_info=err_info,
                                                   err_info_cn=err_info_cn,invalid_index=invalid_index,invalid_index_cn=invalid_index_cn,
                                                          oracle_lock =oracle_lock,oracle_lock_cn=oracle_lock_cn,oracle_pwd =oracle_pwd,oracle_pwd_cn=oracle_pwd_cn,pga=oracle_pga,pga_cn=oracle_pga_cn,archive=oracle_archive,archive_cn=oracle_archive_cn)
            status = 1
        elif request.POST.has_key('logout'):
            logout(request)
            return HttpResponseRedirect('/login/')

    return render_to_response('oracle_servers_add.html', {'status':status})

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
            connect_cn = request.POST.get('connect', None)
            connect = tools.isno(connect_cn)
            tbs_cn = request.POST.get('tbs', None)
            tbs = tools.isno(tbs_cn)
            adg_cn = request.POST.get('adg', None)
            adg = tools.isno(adg_cn)
            temp_tbs_cn = request.POST.get('temp_tbs', None)
            temp_tbs = tools.isno(temp_tbs_cn)
            undo_tbs_cn = request.POST.get('undo_tbs', None)
            undo_tbs = tools.isno(undo_tbs_cn)
            conn_cn = request.POST.get('conn', None)
            conn = tools.isno(conn_cn)
            err_info_cn = request.POST.get('err_info', None)
            err_info = tools.isno(err_info_cn)
            invalid_index_cn = request.POST.get('invalid_index', None)
            invalid_index = tools.isno(invalid_index_cn)
            oracle_lock_cn = request.POST.get('oracle_lock', None)
            oracle_lock = tools.isno(oracle_lock_cn)
            oracle_pwd_cn = request.POST.get('oracle_pwd', None)
            oracle_pwd = tools.isno(oracle_pwd_cn)
            oracle_pga_cn = request.POST.get('oracle_pga', None)
            oracle_pga = tools.isno(oracle_pga_cn)
            oracle_archive_cn = request.POST.get('oracle_archive', None)
            oracle_archive = tools.isno(oracle_archive_cn)
            models_oracle.TabOracleServers.objects.filter(id=rid).update(tags=tags,host=host, port=port, service_name=service_name,
                                                                  user=user, password=password,
                                                                  user_os=user_os, password_os=password_os,
                                                                  connect=connect,
                                                                  connect_cn=connect_cn, tbs=tbs, tbs_cn=tbs_cn,
                                                                  adg=adg, adg_cn=adg_cn, temp_tbs=temp_tbs,
                                                                  temp_tbs_cn=temp_tbs_cn,
                                                                  undo_tbs=undo_tbs, undo_tbs_cn=undo_tbs_cn,
                                                                  conn=conn, conn_cn=conn_cn, err_info=err_info,
                                                                  err_info_cn=err_info_cn,invalid_index=invalid_index,invalid_index_cn=invalid_index_cn,
                                                          oracle_lock =oracle_lock,oracle_lock_cn=oracle_lock_cn,oracle_pwd =oracle_pwd,oracle_pwd_cn=oracle_pwd_cn,pga=oracle_pga,pga_cn=oracle_pga_cn,archive=oracle_archive,archive_cn=oracle_archive_cn)
            status = 1
        elif request.POST.has_key('logout'):
            logout(request)
            return HttpResponseRedirect('/login/')

    return render_to_response('oracle_servers_edit.html',{'oracle_server_edit': oracle_server_edit,'status':status})

@login_required(login_url='/login')
def mysql_servers_add(request):
    status = 0
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    if request.method == "POST":
        if request.POST.has_key('commit'):
            tags = request.POST.get('tags', None)
            host = request.POST.get('host', None)
            port = request.POST.get('port', None)
            user = request.POST.get('user', None)
            password = base64.encodestring(request.POST.get('password', None))
            user_os = request.POST.get('user_os', None)
            password_os = base64.encodestring(request.POST.get('password_os', None))
            connect_cn = request.POST.get('connect', None)
            connect = tools.isno(connect_cn)
            repl_cn = request.POST.get('repl', None)
            repl = tools.isno(repl_cn)
            conn_cn = request.POST.get('conn', None)
            conn = tools.isno(conn_cn)
            err_info_cn = request.POST.get('err_info', None)
            err_info = tools.isno(err_info_cn)
            models_mysql.TabMysqlServers.objects.create(host=host, port=port, tags=tags,
                                                   user=user, password=password,
                                                   user_os=user_os, password_os=password_os, connect=connect,
                                                   connect_cn=connect_cn,
                                                   repl=repl, repl_cn=repl_cn,
                                                   conn=conn, conn_cn=conn_cn, err_info=err_info,
                                                   err_info_cn=err_info_cn)
            status = 1
        elif request.POST.has_key('logout'):
            logout(request)
            return HttpResponseRedirect('/login/')

    return render_to_response('mysql_servers_add.html',{'status':status} )

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
            connect_cn = request.POST.get('connect', None)
            connect = tools.isno(connect_cn)
            repl_cn = request.POST.get('repl', None)
            repl = tools.isno(repl_cn)
            conn_cn = request.POST.get('conn', None)
            conn = tools.isno(conn_cn)
            err_info_cn = request.POST.get('err_info', None)
            err_info = tools.isno(err_info_cn)
            models_mysql.TabMysqlServers.objects.filter(id=rid).update(tags=tags,host=host, port=port,
                                                                  user=user, password=password,
                                                                  user_os=user_os, password_os=password_os,
                                                                  connect=connect,
                                                                  connect_cn=connect_cn,
                                                                  repl=repl, repl_cn=repl_cn,
                                                                  conn=conn, conn_cn=conn_cn, err_info=err_info,
                                                                  err_info_cn=err_info_cn)
            status = 1

        elif request.POST.has_key('logout'):
            logout(request)
            return HttpResponseRedirect('/login/')

    return render_to_response('mysql_servers_edit.html',{'mysql_server_edit': mysql_server_edit,'status':status})

@login_required(login_url='/login')
def show_alarm(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    paginator_msg = Paginator(messageinfo_list, 5)
    page_msg = request.GET.get('page')
    try:
        messageinfos = paginator_msg.page(page_msg)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        messageinfos = paginator_msg.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        messageinfos = paginator_msg.page(paginator_msg.num_pages)

    if request.POST.has_key('logout'):
        logout(request)
        return HttpResponseRedirect('/login/')

    if messageinfo_list:
        msg_num = len(messageinfo_list)
        msg_last = models_frame.TabAlarmInfo.objects.latest('id')
        msg_last_content = msg_last.alarm_content
        tim_last = (datetime.datetime.now() - msg_last.alarm_time).seconds / 60
        return render_to_response('show_alarm.html', {'messageinfos': messageinfos, 'msg_num': msg_num,
                                                   'msg_last_content': msg_last_content, 'tim_last': tim_last})
    else:
        msg_num = 0

        return render_to_response('show_alarm.html', {'messageinfo_list': messageinfo_list,'msg_num': msg_num})

@login_required(login_url='/login')
def recorder(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    recorder_list = models_frame.EventRecorder.objects.order_by('-record_time')
    all_nums = len(recorder_list)
    sys_nums =  len(models_frame.EventRecorder.objects.filter(event_section='系统'))
    db_nums =  len(models_frame.EventRecorder.objects.filter(event_section='数据库'))
    other_nums =  len(models_frame.EventRecorder.objects.filter(event_section='其他'))
    err_nums =  len(models_frame.EventRecorder.objects.filter(event_type='故障'))
    chg_nums =  len(models_frame.EventRecorder.objects.filter(event_type='变更'))
    upg_nums =  len(models_frame.EventRecorder.objects.filter(event_type='升级'))
    if request.method == 'POST':
        logout(request)
        return HttpResponseRedirect('/login/')
    if messageinfo_list:
        msg_num = len(messageinfo_list)
        msg_last = models_frame.TabAlarmInfo.objects.latest('id')
        msg_last_content = msg_last.alarm_content
        tim_last = (datetime.datetime.now() - msg_last.alarm_time).seconds / 60
        return render_to_response('recorder.html',
                                  {'recorder_list': recorder_list,'all_nums':all_nums,'sys_nums':sys_nums,'db_nums':db_nums,'other_nums':other_nums,
                                   'err_nums':err_nums,'chg_nums':chg_nums,'upg_nums':upg_nums, 'messageinfo_list': messageinfo_list,
                                   'msg_num': msg_num,'msg_last_content': msg_last_content, 'tim_last': tim_last})
    else:
        return render_to_response('recorder.html', {'recorder_list': recorder_list})

@login_required(login_url='/login')
def recorder_db(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    recorder_list = models_frame.EventRecorder.objects.order_by('-record_time')
    recorder_db_list = models_frame.EventRecorder.objects.filter(event_section='数据库').order_by('-record_time')
    all_nums = len(recorder_list)
    sys_nums =  len(models_frame.EventRecorder.objects.filter(event_section='系统'))
    db_nums =  len(models_frame.EventRecorder.objects.filter(event_section='数据库'))
    other_nums =  len(models_frame.EventRecorder.objects.filter(event_section='其他'))
    err_nums =  len(models_frame.EventRecorder.objects.filter(event_type='故障'))
    chg_nums =  len(models_frame.EventRecorder.objects.filter(event_type='变更'))
    upg_nums =  len(models_frame.EventRecorder.objects.filter(event_type='升级'))

    if request.method == 'POST':
        logout(request)
        return HttpResponseRedirect('/login/')

    if messageinfo_list:
        msg_num = len(messageinfo_list)
        msg_last = models_frame.TabAlarmInfo.objects.latest('id')
        msg_last_content = msg_last.alarm_content
        tim_last = (datetime.datetime.now() - msg_last.alarm_time).seconds / 60
        return render_to_response('recorder.html',
                                  {'recorder_list': recorder_db_list,'all_nums':all_nums,'sys_nums':sys_nums,'db_nums':db_nums,'other_nums':other_nums,
                                   'err_nums':err_nums,'chg_nums':chg_nums,'upg_nums':upg_nums, 'messageinfo_list': messageinfo_list,
                                   'msg_num': msg_num,'msg_last_content': msg_last_content, 'tim_last': tim_last})
    else:
        return render_to_response('recorder.html', {'recorder_list': recorder_db_list})

@login_required(login_url='/login')
def recorder_os(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    recorder_list = models_frame.EventRecorder.objects.order_by('-record_time')
    recorder_os_list = models_frame.EventRecorder.objects.filter(event_section='系统').order_by('-record_time')
    all_nums = len(recorder_list)
    sys_nums =  len(models_frame.EventRecorder.objects.filter(event_section='系统'))
    db_nums =  len(models_frame.EventRecorder.objects.filter(event_section='数据库'))
    other_nums =  len(models_frame.EventRecorder.objects.filter(event_section='其他'))
    err_nums =  len(models_frame.EventRecorder.objects.filter(event_type='故障'))
    chg_nums =  len(models_frame.EventRecorder.objects.filter(event_type='变更'))
    upg_nums =  len(models_frame.EventRecorder.objects.filter(event_type='升级'))

    if request.method == 'POST':
        logout(request)
        return HttpResponseRedirect('/login/')

    if messageinfo_list:
        msg_num = len(messageinfo_list)
        msg_last = models_frame.TabAlarmInfo.objects.latest('id')
        msg_last_content = msg_last.alarm_content
        tim_last = (datetime.datetime.now() - msg_last.alarm_time).seconds / 60
        return render_to_response('recorder.html',
                                  {'recorder_list': recorder_os_list,'all_nums':all_nums,'sys_nums':sys_nums,'db_nums':db_nums,'other_nums':other_nums,
                                   'err_nums':err_nums,'chg_nums':chg_nums,'upg_nums':upg_nums, 'messageinfo_list': messageinfo_list,
                                   'msg_num': msg_num,'msg_last_content': msg_last_content, 'tim_last': tim_last})
    else:
        return render_to_response('recorder.html', {'recorder_list': recorder_os_list})

@login_required(login_url='/login')
def recorder_others(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    recorder_list = models_frame.EventRecorder.objects.order_by('-record_time')
    recorder_others_list = models_frame.EventRecorder.objects.filter(event_section='其他').order_by('-record_time')
    all_nums = len(recorder_list)
    sys_nums =  len(models_frame.EventRecorder.objects.filter(event_section='系统'))
    db_nums =  len(models_frame.EventRecorder.objects.filter(event_section='数据库'))
    other_nums =  len(models_frame.EventRecorder.objects.filter(event_section='其他'))
    err_nums =  len(models_frame.EventRecorder.objects.filter(event_type='故障'))
    chg_nums =  len(models_frame.EventRecorder.objects.filter(event_type='变更'))
    upg_nums =  len(models_frame.EventRecorder.objects.filter(event_type='升级'))

    if request.method == 'POST':
        logout(request)
        return HttpResponseRedirect('/login/')

    if messageinfo_list:
        msg_num = len(messageinfo_list)
        msg_last = models_frame.TabAlarmInfo.objects.latest('id')
        msg_last_content = msg_last.alarm_content
        tim_last = (datetime.datetime.now() - msg_last.alarm_time).seconds / 60
        return render_to_response('recorder.html',
                                  {'recorder_list': recorder_others_list,'all_nums':all_nums,'sys_nums':sys_nums,'db_nums':db_nums,'other_nums':other_nums,
                                   'err_nums':err_nums,'chg_nums':chg_nums,'upg_nums':upg_nums, 'messageinfo_list': messageinfo_list,
                                   'msg_num': msg_num,'msg_last_content': msg_last_content, 'tim_last': tim_last})
    else:
        return render_to_response('recorder.html', {'recorder_list': recorder_others_list})

@login_required(login_url='/login')
def recorder_err(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    recorder_list = models_frame.EventRecorder.objects.order_by('-record_time')
    recorder_err_list = models_frame.EventRecorder.objects.filter(event_type='故障').order_by('-record_time')
    all_nums = len(recorder_list)
    sys_nums =  len(models_frame.EventRecorder.objects.filter(event_section='系统'))
    db_nums =  len(models_frame.EventRecorder.objects.filter(event_section='数据库'))
    other_nums =  len(models_frame.EventRecorder.objects.filter(event_section='其他'))
    err_nums =  len(models_frame.EventRecorder.objects.filter(event_type='故障'))
    chg_nums =  len(models_frame.EventRecorder.objects.filter(event_type='变更'))
    upg_nums =  len(models_frame.EventRecorder.objects.filter(event_type='升级'))

    if request.method == 'POST':
        logout(request)
        return HttpResponseRedirect('/login/')

    if messageinfo_list:
        msg_num = len(messageinfo_list)
        msg_last = models_frame.TabAlarmInfo.objects.latest('id')
        msg_last_content = msg_last.alarm_content
        tim_last = (datetime.datetime.now() - msg_last.alarm_time).seconds / 60
        return render_to_response('recorder.html',
                                  {'recorder_list': recorder_err_list,'all_nums':all_nums,'sys_nums':sys_nums,'db_nums':db_nums,'other_nums':other_nums,
                                   'err_nums':err_nums,'chg_nums':chg_nums,'upg_nums':upg_nums, 'messageinfo_list': messageinfo_list,
                                   'msg_num': msg_num,'msg_last_content': msg_last_content, 'tim_last': tim_last})
    else:
        return render_to_response('recorder.html', {'recorder_list': recorder_err_list})

@login_required(login_url='/login')
def recorder_chg(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    recorder_list = models_frame.EventRecorder.objects.order_by('-record_time')
    recorder_chg_list = models_frame.EventRecorder.objects.filter(event_type='变更').order_by('-record_time')
    all_nums = len(recorder_list)
    sys_nums =  len(models_frame.EventRecorder.objects.filter(event_section='系统'))
    db_nums =  len(models_frame.EventRecorder.objects.filter(event_section='数据库'))
    other_nums =  len(models_frame.EventRecorder.objects.filter(event_section='其他'))
    err_nums =  len(models_frame.EventRecorder.objects.filter(event_type='故障'))
    chg_nums =  len(models_frame.EventRecorder.objects.filter(event_type='变更'))
    upg_nums =  len(models_frame.EventRecorder.objects.filter(event_type='升级'))

    if request.method == 'POST':
        logout(request)
        return HttpResponseRedirect('/login/')

    if messageinfo_list:
        msg_num = len(messageinfo_list)
        msg_last = models_frame.TabAlarmInfo.objects.latest('id')
        msg_last_content = msg_last.alarm_content
        tim_last = (datetime.datetime.now() - msg_last.alarm_time).seconds / 60
        return render_to_response('recorder.html',
                                  {'recorder_list': recorder_chg_list,'all_nums':all_nums,'sys_nums':sys_nums,'db_nums':db_nums,'other_nums':other_nums,
                                   'err_nums':err_nums,'chg_nums':chg_nums,'upg_nums':upg_nums, 'messageinfo_list': messageinfo_list,
                                   'msg_num': msg_num,'msg_last_content': msg_last_content, 'tim_last': tim_last})
    else:
        return render_to_response('recorder.html', {'recorder_list': recorder_chg_list})

@login_required(login_url='/login')
def recorder_upd(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    recorder_list = models_frame.EventRecorder.objects.order_by('-record_time')
    recorder_upd_list = models_frame.EventRecorder.objects.filter(event_type='升级').order_by('-record_time')
    all_nums = len(recorder_list)
    sys_nums =  len(models_frame.EventRecorder.objects.filter(event_section='系统'))
    db_nums =  len(models_frame.EventRecorder.objects.filter(event_section='数据库'))
    other_nums =  len(models_frame.EventRecorder.objects.filter(event_section='其他'))
    err_nums =  len(models_frame.EventRecorder.objects.filter(event_type='故障'))
    chg_nums =  len(models_frame.EventRecorder.objects.filter(event_type='变更'))
    upg_nums =  len(models_frame.EventRecorder.objects.filter(event_type='升级'))

    if request.method == 'POST':
        logout(request)
        return HttpResponseRedirect('/login/')

    if messageinfo_list:
        msg_num = len(messageinfo_list)
        msg_last = models_frame.TabAlarmInfo.objects.latest('id')
        msg_last_content = msg_last.alarm_content
        tim_last = (datetime.datetime.now() - msg_last.alarm_time).seconds / 60
        return render_to_response('recorder.html',
                                  {'recorder_list': recorder_upd_list,'all_nums':all_nums,'sys_nums':sys_nums,'db_nums':db_nums,'other_nums':other_nums,
                                   'err_nums':err_nums,'chg_nums':chg_nums,'upg_nums':upg_nums, 'messageinfo_list': messageinfo_list,
                                   'msg_num': msg_num,'msg_last_content': msg_last_content, 'tim_last': tim_last})
    else:
        return render_to_response('recorder.html', {'recorder_list': recorder_upd_list})

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



    return render_to_response('recorder_add.html',
                                  {'recorder_list': recorder_list, 'all_nums': all_nums, 'sys_nums': sys_nums,
                                   'db_nums': db_nums, 'other_nums': other_nums,
                                   'err_nums': err_nums, 'chg_nums': chg_nums, 'upg_nums': upg_nums,'status':status})



@login_required(login_url='/login')
def sys_setting(request):
    # 读配置文件
    conf = ConfigParser.ConfigParser()
    conf_path = os.getcwd() + '/check_alarm/config/db_monitor.conf'
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
        return render_to_response('sys_setting.html',
                                  {'messageinfo_list': messageinfo_list, 'msg_num': msg_num,
                                   'msg_last_content': msg_last_content, 'tim_last': tim_last,
                                   'sender': sender,'smtpserver':smtpserver,'username':username,
                                   'password_email': password_email,'receiver':receiver,'msg_from':msg_from,
                                   'check_sleep_time':check_sleep_time,'alarm_sleep_time':alarm_sleep_time,
                                   'next_send_email_time':next_send_email_time,'host':host,'port':port,'user':user,
                                   'password_mysql': password_mysql,'dbname':dbname,'now':now})
    else:
        return render_to_response('sys_setting.html', {'messageinfo_list': messageinfo_list,
                                   'sender': sender,'smtpserver':smtpserver,'username':username,
                                   'password_email': password_email,'receiver':receiver,'msg_from':msg_from,
                                   'check_sleep_time':check_sleep_time,'alarm_sleep_time':alarm_sleep_time,
                                   'next_send_email_time':next_send_email_time,'host':host,'port':port,'user':user,
                                   'password_mysql': password_mysql,'dbname':dbname,'now':now} )

@login_required(login_url='/login')
def my_check(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
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
            select_form = request.POST.get('select_form', None)
            # begin_time = (datetime.datetime.now() - datetime.timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S")
            begin_time = tools.range(date_range)
            end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            file_tag = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            check_file_name  = 'oracheck_' + file_tag +  '.xls'
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
        return render_to_response('my_check.html', { 'messageinfo_list': messageinfo_list,'msg_num':msg_num,'now':now,
                                                   'msg_last_content': msg_last_content, 'tim_last': tim_last,
                                                     'select_type':select_type,'date_range':date_range,'select_tags':select_tags,'select_form':select_form,'file_tag':file_tag,'check_err':check_err,'begin_time':begin_time,'end_time':end_time})
    else:
        msg_num = 0
        msg_last_content = ''
        tim_last = ''
        return render_to_response('my_check.html',
                                  {'messageinfo_list': messageinfo_list,'now': now,
                                   'msg_last_content': msg_last_content, 'tim_last': tim_last,
                                   'select_type': select_type, 'date_range': date_range, 'select_tags': select_tags,
                                   'select_form': select_form,'file_tag':file_tag,'check_err':check_err,'begin_time':begin_time,'end_time':end_time})


def page_not_found(request):
    return render(request, '404.html')


def download(request):
    select_form = request.GET.get('select_form')
    file_tag = request.GET.get('file_tag')
    file_path = os.getcwd() + '\check_result' + '\\'
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
        return render_to_response('my_tools.html', { 'messageinfo_list': messageinfo_list,
                                                   'msg_num': msg_num,'now':now,
                                                   'msg_last_content': msg_last_content, 'tim_last': tim_last})
    else:
        msg_num = 0
        msg_last_content = ''
        tim_last = ''
        return render_to_response('my_tools.html',
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
    return render(request,'log_collect.html', {'messageinfo_list': messageinfo_list, 'log_collects': log_collects,
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


    return render_to_response('log_collects_edit.html', {'log_collect_edit': log_collect_edit,'status':status})

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

    return render_to_response('log_collects_add.html',{'status':status})

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
        return render_to_response('easy_start.html', { 'messageinfo_list': messageinfo_list,'easy_starts':easy_starts,
                                                   'msg_num': msg_num,'now':now,
                                                   'msg_last_content': msg_last_content, 'tim_last': tim_last})
    else:
        msg_num = 0
        msg_last_content = ''
        tim_last = ''
        return render_to_response('easy_start.html',
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

    return render_to_response('easy_starts_edit.html', {'easy_start_edit': easy_start_edit,'status':status})

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

    return render_to_response('easy_starts_add.html', {'status':status})

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
    paginator_log = Paginator(log_info, 10)
    page_log = request.GET.get('page_log')
    try:
        logs = paginator_log.page(page_log)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        logs = paginator_log.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        logs = paginator_log.page(paginator_log.num_pages)
    now = tools.now()

    if request.method == 'POST':
        logout(request)
        return HttpResponseRedirect('/login/')

    if messageinfo_list:
        msg_num = len(messageinfo_list)
        msg_last = models_frame.TabAlarmInfo.objects.latest('id')
        msg_last_content = msg_last.alarm_content
        tim_last = (datetime.datetime.now() - msg_last.alarm_time).seconds / 60
        return render_to_response('log_info.html', {'messageinfo_list': messageinfo_list, 'logs':logs,
                                                   'msg_num': msg_num,'now':now,
                                                   'msg_last_content': msg_last_content, 'tim_last': tim_last})
    else:
        msg_num = 0
        msg_last_content = ''
        tim_last = ''
        return render_to_response('log_info.html',
                                  {'messageinfo_list': messageinfo_list, 'logs':logs,'now': now,
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
        return render_to_response('oracle_install.html',
                                  {'messageinfo_list': messageinfo_list, 'msg_num': msg_num,
                                   'msg_last_content': msg_last_content, 'tim_last': tim_last})
    else:
        return render_to_response('oracle_install.html', )

@login_required(login_url='/login')
def mysql_install(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    if request.method == "POST":
        if request.POST.has_key('commit'):
            host_name = request.POST.get('host_name', None)
            host = request.POST.get('host', None)
            password = request.POST.get('password', None)
            linux_version = request.POST.get('linux_version', None)
            mysql_version = request.POST.get('oracle_version', None)
            soft_dir = request.POST.get('soft_dir', None)
            data_dir = request.POST.get('data_dir', None)

            task.mysql_install.delay(host,'root',password)
            log_type = 'Mysql部署'
            return HttpResponseRedirect('/log_info?log_type=%s' % log_type)

        elif request.POST.has_key('logout'):
            logout(request)
            return HttpResponseRedirect('/login/')

    if messageinfo_list:
        msg_num = len(messageinfo_list)
        msg_last = models_frame.TabAlarmInfo.objects.latest('id')
        msg_last_content = msg_last.alarm_content
        tim_last = (datetime.datetime.now() - msg_last.alarm_time).seconds / 60
        return render_to_response('mysql_install.html',
                                  {'messageinfo_list': messageinfo_list, 'msg_num': msg_num,
                                   'msg_last_content': msg_last_content, 'tim_last': tim_last})
    else:
        return render_to_response('mysql_install.html', )


def oracle_ctl(request):
    # 告警
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    oper_type = request.GET.get('oper_type')
    host = request.GET.get('host')
    tags = request.GET.get('tags')

    if oper_type:
        sql = '''select user,password from tab_linux_servers where host='%s' ''' % host
        oracle = tools.mysql_query(sql)
        user = oracle[0][0]
        password = oracle[0][1]
        password = base64.decodestring(password)
        if oper_type == 'startup':
            task.oracle_startup.delay(tags,host, user, password)
            messages.add_message(request,messages.INFO,'正在启动' )
        elif oper_type == 'shutdown':
            task.oracle_shutdown.delay(tags,host, user, password)
            messages.add_message(request,messages.INFO,'正在关闭')
        else:
            task.oracle_restart.delay(tags, host, user, password)
            messages.add_message(request,messages.INFO,'正在重启')

    # 数据库操作面板
    oracle_ctl_sql = '''select t1.tags,
               t1.host,
               t1.port,
               t1.service_name,
               (case t2.mon_status
               when 'connected' then 'running' else 'suspend' end) run_status,
               (case t2.mon_status
               when 'connected' then 'success' else 'danger' end) is_run,
                 (case t2.mon_status
               when 'connected' then 'red' else 'green' end) run_color,
               (case t2.mon_status
               when 'connected' then 'shutdown' else 'startup' end) oper_type
          from tab_oracle_servers t1
          left join oracle_db t2
            on t1.tags = t2.tags'''

    oracle_ctl_list = tools.mysql_django_query(oracle_ctl_sql)

    paginator_oracle_ctl = Paginator(oracle_ctl_list, 5)
    page_oracle_ctl = request.GET.get('page_oracle_ctl')
    try:
        oracle_ctls = paginator_oracle_ctl.page(page_oracle_ctl)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        oracle_ctls = paginator_oracle_ctl.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        oracle_ctls = paginator_oracle_ctl.page(page_oracle_ctl.num_pages)

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
    return render(request,'oracle_ctl.html',
                              {'messageinfo_list': messageinfo_list, 'oracle_ctls': oracle_ctls,
                               'msg_num': msg_num, 'now': now,
                               'msg_last_content': msg_last_content, 'tim_last': tim_last}
                              )



def mysql_ctl(request):
    # 告警
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    oper_type = request.GET.get('oper_type')
    host = request.GET.get('host')

    if oper_type:
        log_type = 'Mysql启停'
        sql = '''select user,password from tab_linux_servers where host='%s' ''' % host
        mysql = tools.mysql_query(sql)
        user = mysql[0][0]
        password = mysql[0][1]
        password = base64.decodestring(password)
        if oper_type == 'startup':
            # ora_do.oracle_startup(host, user, password)
            return HttpResponseRedirect('/mysql_ctl/')
        elif oper_type == 'shutdown':
            # ora_do.oracle_shutdown(host, user, password)
            return HttpResponseRedirect('/mysql_ctl/')
        else:
            # ora_do.oracle_shutdown(host, user, password)
            # ora_do.oracle_startup(host, user, password)
            return HttpResponseRedirect('/mysql_ctl/')
    else:
        # 数据库操作面板
        mysql_ctl_sql = '''select t1.tags,
             t1.host,
             t1.port,
             (case t2.mon_status
             when 'connected' then 'running' else 'suspend' end) run_status,
             (case t2.mon_status
             when 'connected' then 'success' else 'danger' end) is_run,
               (case t2.mon_status
             when 'connected' then 'red' else 'green' end) run_color,
             (case t2.mon_status
             when 'connected' then 'shutdown' else 'startup' end) oper_type
        from tab_mysql_servers t1
        left join mysql_db t2
          on t1.tags = t2.tags'''

        mysql_ctl_list = tools.mysql_django_query(mysql_ctl_sql)

        paginator_mysql_ctl = Paginator(mysql_ctl_list, 5)
        page_mysql_ctl = request.GET.get('page_mysql_ctl')
        try:
            mysql_ctls = paginator_mysql_ctl.page(page_mysql_ctl)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            mysql_ctls = paginator_mysql_ctl.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            mysql_ctls = paginator_mysql_ctl.page(page_mysql_ctl.num_pages)

        now = tools.now()
        if request.method == 'POST':
            logout(request)
            return HttpResponseRedirect('/login/')

        if messageinfo_list:
            msg_num = len(messageinfo_list)
            msg_last = models_frame.TabAlarmInfo.objects.latest('id')
            msg_last_content = msg_last.alarm_content
            tim_last = (datetime.datetime.now() - msg_last.alarm_time).seconds / 60
            return render_to_response('mysql_ctl.html',
                                      {'messageinfo_list': messageinfo_list, 'mysql_ctls': mysql_ctls,
                                       'msg_num': msg_num, 'now': now,
                                       'msg_last_content': msg_last_content, 'tim_last': tim_last})
        else:
            msg_num = 0
            msg_last_content = ''
            tim_last = ''
            return render_to_response('mysql_ctl.html',
                                      {'messageinfo_list': messageinfo_list, 'mysql_ctls': mysql_ctls, 'now': now,
                                       'msg_last_content': msg_last_content, 'tim_last': tim_last})



@login_required(login_url='/login')
def sql_exec(request):
    # 告警
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()

    sql_list = models_frame.SqlList.objects.all()
    paginator_sql = Paginator(sql_list, 5)
    page_sql = request.GET.get('page_sql')
    try:
        sqls = paginator_sql.page(page_sql)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        sqls = paginator_sql.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        sqls = paginator_sql.page(paginator_sql.num_pages)
    now = tools.now()
    log_type = 'Oracle执行sql脚本'
    if request.method == 'POST':
        local_dir = os.getcwd()
        if request.POST.has_key('go_start'):
            tools.my_log(log_type, '开始执行sql脚本！', '')
            task.oracle_exec_sql.delay()
            messages.add_message(request,messages.INFO,'正在执行')
        elif request.POST.has_key('reset'):
            cmd = 'rm %s/frame/sqlscripts/*.sql' %local_dir
            status, result = commands.getstatusoutput(cmd)
            models_frame.SqlList.objects.filter().delete()
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
    return render(request,'sql_exec.html',
                              {'messageinfo_list': messageinfo_list, 'sqls': sqls, 'log_type': log_type,
                               'msg_num': msg_num, 'now': now,
                               'msg_last_content': msg_last_content, 'tim_last': tim_last})



@login_required(login_url='/login')
def upload_file(request):
    local_dir = os.getcwd()
    log_type = 'Oracle执行sql脚本'
    tools.mysql_exec("delete from many_logs where log_type = 'Oracle执行sql脚本'", '')
    if request.method == "POST":    # 请求方法为POST时，进行处理
        files = request.FILES.getlist('myfile')
        for f in files:
            destination = open(os.path.join("%s/frame/sqlscripts" %local_dir, f.name),
                               'wb+')  # 打开特定的文件进行二进制的写操作
            for chunk in f.chunks():  # 分块写入文件
                destination.write(chunk)
            destination.close()
        # 执行sql脚本列表
        cmd = 'ls %s/frame/sqlscripts/*.sql' %local_dir
        status, result = commands.getstatusoutput(cmd)
        sql_list = result.split('\n')
        tools.my_log(log_type, '上传脚本成功！', '')
        # 将脚本信息写进数据库
        for sql in sql_list:
            sqlfile = file(sql, 'a+')
            sqlfile.write('exit')
            sqlfile.close()
            sql_name = sql.split('/')[-1]
            sql_no = sql_name.split('_')[0]
            db_name = sql_name.split('_')[1]
            models_frame.SqlList.objects.create(sql_no=sql_no, sql_info=sql,sql_name=sql_name,db_name=db_name,result='未执行',result_color='')
        tools.my_log(log_type, '脚本初始化完成！', '')
        return HttpResponseRedirect('/sql_exec/')

@login_required(login_url='/login')
def oracle_lock_manage(request):
    # 告警
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()


    oracle_lock_list =  models_oracle.OracleLock.objects.all()

    paginator_oracle_lock = Paginator(oracle_lock_list, 5)
    page_oracle_lock = request.GET.get('page_oracle_lock')
    try:
        oracle_lockss = paginator_oracle_lock.page(page_oracle_lock)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        oracle_locks = paginator_oracle_lock.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        oracle_locks = paginator_oracle_lock.page(page_oracle_lock.num_pages)

    now = tools.now()
    if request.method == 'POST':
        logout(request)
        return HttpResponseRedirect('/login/')

    if messageinfo_list:
        msg_num = len(messageinfo_list)
        msg_last = models_frame.TabAlarmInfo.objects.latest('id')
        msg_last_content = msg_last.alarm_content
        tim_last = (datetime.datetime.now() - msg_last.alarm_time).seconds / 60
        return render_to_response('oracle_lock_manage.html',
                                  {'messageinfo_list': messageinfo_list, 'oracle_locks': oracle_locks,
                                   'msg_num': msg_num, 'now': now,
                                   'msg_last_content': msg_last_content, 'tim_last': tim_last})
    else:
        msg_num = 0
        msg_last_content = ''
        tim_last = ''
        return render_to_response('oracle_lock_manage.html',
                                  {'messageinfo_list': messageinfo_list, 'oracle_locks': oracle_locks, 'now': now,
                                   'msg_last_content': msg_last_content, 'tim_last': tim_last})

@login_required(login_url='/login')
def oracle_session(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    tags = request.GET.get('tags')
    session_id = request.GET.get('session_id')
    sql = "select host,port,service_name,user,password,user_os,password_os from tab_oracle_servers where tags= '%s' " %tags
    oracle = tools.mysql_query(sql)
    host = oracle[0][0]
    port = oracle[0][1]
    service_name = oracle[0][2]
    user = oracle[0][3]
    password = oracle[0][4]
    password = base64.decodestring(password)
    url = host + ':' + port + '/' + service_name
    sql = '''select nvl(s.username, 'None') oracle_user,
       s.logon_time,
       p.username unix_user,
       s.sid,
       s.serial# serial,
       p.spid unix_pid,
       s.status,
       s.process,
       s.osuser,
       s.program,
       s.module,
       s.machine,
       s.event,
       l.SQL_TEXT,
       s.sql_id,
       s.prev_sql_id,
'ps -ef|grep '|| p.spid ||'|grep LOCAL=NO|awk ''{print $2}''|xargs kill -9' kill_sh
  from v$process p, v$session s, v$sql l
 where s.paddr = p.addr and s.SQL_ADDRESS = l.ADDRESS(+)
   and s.SQL_HASH_VALUE = l.HASH_VALUE(+)
   and s.sql_child_number = l.child_number(+)
   and s.sid = %s''' %session_id

    oracle_sessions = tools.oracle_django_query(user,password,url,sql)

    now = tools.now()
    if request.method == 'POST':
        logout(request)
        return HttpResponseRedirect('/login/')

    if messageinfo_list:
        msg_num = len(messageinfo_list)
        msg_last = models_frame.TabAlarmInfo.objects.latest('id')
        msg_last_content = msg_last.alarm_content
        tim_last = (datetime.datetime.now() - msg_last.alarm_time).seconds / 60
        return render_to_response('oracle_session.html',
                                  {'messageinfo_list': messageinfo_list, 'oracle_sessions': oracle_sessions,'tags':tags,
                                   'msg_num': msg_num, 'now': now,
                                   'msg_last_content': msg_last_content, 'tim_last': tim_last})
    else:
        msg_num = 0
        msg_last_content = ''
        tim_last = ''
        return render_to_response('oracle_session.html',
                                  {'messageinfo_list': messageinfo_list, 'oracle_sessions': oracle_sessions, 'tags':tags,'now': now,
                                   'msg_last_content': msg_last_content, 'tim_last': tim_last})

@login_required(login_url='/login')
def kill_session(request):
    tags = request.GET.get('tags')
    session_id = request.GET.get('session_id')
    kill_sh = request.GET.get('kill_sh')
    sql = "select host,user_os,password_os from tab_oracle_servers where tags= '%s' " %tags
    oracle = tools.mysql_query(sql)
    host = oracle[0][0]
    user_os = oracle[0][1]
    password_os = oracle[0][2]
    password_os = base64.decodestring(password_os)
    tools.exec_command(host=host,user=user_os,password=password_os,command=kill_sh)
    return HttpResponseRedirect('/oracle_session?tags=%s&session_id=%s' %(tags,session_id))

@login_required(login_url='/login')
def oracle_process(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    tags = request.GET.get('tags')
    sql = "select host,port,service_name,user,password,user_os,password_os from tab_oracle_servers where tags= '%s' " % tags
    oracle = tools.mysql_query(sql)
    host = oracle[0][0]
    port = oracle[0][1]
    service_name = oracle[0][2]
    user = oracle[0][3]
    password = oracle[0][4]
    password = base64.decodestring(password)
    url = host + ':' + port + '/' + service_name
    sql = '''select a.USERNAME, a.OSUSER, a.MACHINE, a.PROGRAM,a.STATUS, count(1) CNT
       from v$session a where a.USERNAME is not null
    group by a.USERNAME, a.OSUSER, a.MACHINE,a.PROGRAM, a.STATUS
      order by count(1) desc'''
    oracle_process_list = tools.oracle_django_query(user, password, url, sql)
    paginator_oracle_process = Paginator(oracle_process_list, 5)
    page_oracle_process = request.GET.get('page_oracle_process')
    try:
        oracle_processes = paginator_oracle_process.page(page_oracle_process)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        oracle_processes = paginator_oracle_process.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        oracle_processes = paginator_oracle_process.page(page_oracle_process.num_pages)
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
    return render_to_response('oracle_process.html',
                              {'messageinfo_list': messageinfo_list, 'oracle_processes': oracle_processes,
                               'tags': tags,
                               'msg_num': msg_num, 'now': now,
                               'msg_last_content': msg_last_content, 'tim_last': tim_last})

@login_required(login_url='/login')
def oracle_undo(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    tags = request.GET.get('tags')
    sql = "select host,port,service_name,user,password,user_os,password_os from tab_oracle_servers where tags= '%s' " % tags
    oracle = tools.mysql_query(sql)
    host = oracle[0][0]
    port = oracle[0][1]
    service_name = oracle[0][2]
    user = oracle[0][3]
    password = oracle[0][4]
    password = base64.decodestring(password)
    url = host + ':' + port + '/' + service_name
    # undo使用情况
    sql_undo = '''select tablespace_name, status, sum(bytes) / 1024 / 1024 MB
              from dba_undo_extents
             where tablespace_name like 'UNDOTBS%'
             group by tablespace_name, status
             order by 1'''
    oracle_undos = tools.oracle_django_query(user, password, url, sql_undo)
    # session undo
    sql_session_undo = '''select  r.name rbs,nvl(s.username, 'None') oracle_user, s.osuser client_user,p.username unix_user,s.program,s.sid,s.serial#,p.spid unix_pid,t.used_ublk * TO_NUMBER(x.value) / 1024 / 1024 as undo_mb,TO_CHAR(s.logon_time, 'mm/dd/yy hh24:mi:ss') as login_time,TO_CHAR(sysdate - (s.last_call_et) / 86400, 'mm/dd/yy hh24:mi:ss') as last_txn,t.START_TIME transaction_starttime from v$process p, v$rollname r,v$session s,v$transaction t,v$parameter x where s.taddr = t.addr and s.paddr = p.addr and r.usn = t.xidusn(+) and x.name = 'db_block_size' ORDER by undo_mb'''
    oracle_session_undo_list = tools.oracle_django_query(user, password, url, sql_session_undo)
    paginator_oracle_session_undo = Paginator(oracle_session_undo_list, 5)
    page_oracle_session_undo = request.GET.get('page_oracle_session_undo')
    try:
        oracle_session_undos = paginator_oracle_session_undo.page(page_oracle_session_undo)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        oracle_session_undos = paginator_oracle_session_undo.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        oracle_session_undos = paginator_oracle_session_undo.page(page_oracle_session_undo.num_pages)
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
    return render_to_response('oracle_undo.html',
                              {'messageinfo_list': messageinfo_list, 'oracle_undos': oracle_undos,'oracle_session_undos':oracle_session_undos,
                               'tags': tags,
                               'msg_num': msg_num, 'now': now,
                               'msg_last_content': msg_last_content, 'tim_last': tim_last})

@login_required(login_url='/login')
def oracle_temp(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    tags = request.GET.get('tags')
    sql = "select host,port,service_name,user,password,user_os,password_os from tab_oracle_servers where tags= '%s' " % tags
    oracle = tools.mysql_query(sql)
    host = oracle[0][0]
    port = oracle[0][1]
    service_name = oracle[0][2]
    user = oracle[0][3]
    password = oracle[0][4]
    password = base64.decodestring(password)
    url = host + ':' + port + '/' + service_name
    # session temp
    sql_session_temp = '''SELECT S.sid sid,S.username,S.osuser,P.spid,S.module,S.program,SUM(T.blocks) * TBS.block_size / 1024/1024  mb_used,T.tablespace,COUNT(*) sort_ops FROM v$sort_usage T, v$session S, dba_tablespaces TBS, v$process P WHERE T.session_addr = S.saddr AND S.paddr = P.addr AND T.tablespace = TBS.tablespace_name GROUP BY S.sid,S.serial#,S.username,S.osuser,P.spid,S.module,S.program,TBS.block_size,T.tablespace ORDER BY sid'''
    oracle_session_temp_list = tools.oracle_django_query(user, password, url, sql_session_temp)
    paginator_oracle_session_temp = Paginator(oracle_session_temp_list, 5)
    page_oracle_session_temp = request.GET.get('page_oracle_session_temp')
    try:
        oracle_session_temps = paginator_oracle_session_temp.page(page_oracle_session_temp)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        oracle_session_temps = paginator_oracle_session_temp.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        oracle_session_temps = paginator_oracle_session_temp.page(page_oracle_session_temp.num_pages)
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
    return render_to_response('oracle_temp.html',
                              {'messageinfo_list': messageinfo_list,'oracle_session_temps':oracle_session_temps,
                               'tags': tags,
                               'msg_num': msg_num, 'now': now,
                               'msg_last_content': msg_last_content, 'tim_last': tim_last})

@login_required(login_url='/login')
def oracle_active_session(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    tags = request.GET.get('tags')
    sql = "select host,port,service_name,user,password,user_os,password_os from tab_oracle_servers where tags= '%s' " % tags
    oracle = tools.mysql_query(sql)
    host = oracle[0][0]
    port = oracle[0][1]
    service_name = oracle[0][2]
    user = oracle[0][3]
    password = oracle[0][4]
    password = base64.decodestring(password)
    url = host + ':' + port + '/' + service_name
    # session temp
    sql_active_session = '''select to_char(a.logon_time, 'yyyy-mm-dd hh24:mi') logon_time,
       a.sql_id,
       a.event,
       a.BLOCKING_SESSION,
       a.username,
       a.osuser,
       a.process,
       a.machine,
       a.program,
       a.module,
       substr(b.sql_text,1,100) sql_text,
       b.LAST_LOAD_TIME,
       to_char(b.last_active_time, 'yyyy-mm-dd hh24:mi:ss') last_active_time,
       c.owner,
       c.object_name,
       a.last_call_et,
       a.sid,
       a.SQL_CHILD_NUMBER,
       c.object_type,
       p.PGA_ALLOC_MEM,
       a.p1,
       a.p2,
       a.p3,
       'kill -9 ' || p.spid killstr,
'ps -ef|grep '|| p.spid ||'|grep LOCAL=NO|awk ''{print $2}''|xargs kill -9' kill_sh
  from v$session a, v$sql b, dba_objects c, v$process p
 where a.status = 'ACTIVE'
   and p.addr = a.paddr
   and a.sql_id = b.sql_id(+)
  -- and a.wait_class <> 'Idle'
   and a.sql_child_number = b.CHILD_NUMBER(+)
   and a.row_wait_obj# = c.object_id(+)
   and a.type = 'USER'
 order by a.sql_id, a.event'''
    oracle_active_session_list = tools.oracle_django_query(user, password, url, sql_active_session)
    paginator_oracle_active_session = Paginator(oracle_active_session_list, 5)
    page_oracle_active_session = request.GET.get('page_oracle_active_session')
    try:
        oracle_active_sessions = paginator_oracle_active_session.page(page_oracle_active_session)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        oracle_active_sessions = paginator_oracle_active_session.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        oracle_active_sessions = paginator_oracle_active_session.page(page_oracle_active_session.num_pages)
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
    return render_to_response('oracle_active_session.html',
                              {'messageinfo_list': messageinfo_list,'oracle_active_sessions':oracle_active_sessions,
                               'tags': tags,
                               'msg_num': msg_num, 'now': now,
                               'msg_last_content': msg_last_content, 'tim_last': tim_last})

@login_required(login_url='/login')
def oracle_waiting_session(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    tags = request.GET.get('tags')
    sql = "select host,port,service_name,user,password,user_os,password_os from tab_oracle_servers where tags= '%s' " % tags
    oracle = tools.mysql_query(sql)
    host = oracle[0][0]
    port = oracle[0][1]
    service_name = oracle[0][2]
    user = oracle[0][3]
    password = oracle[0][4]
    password = base64.decodestring(password)
    url = host + ':' + port + '/' + service_name
    # session temp
    sql_waiting_session = '''select inst_id,sid, username, event, blocking_session,
	seconds_in_wait, wait_time
	from gv$session where state in ('WAITING')
	and wait_class != 'Idle' '''

    oracle_waiting_session_list = tools.oracle_django_query(user, password, url, sql_waiting_session)
    paginator_oracle_waiting_session = Paginator(oracle_waiting_session_list, 5)
    page_oracle_waiting_session = request.GET.get('page_oracle_waiting_session')
    try:
        oracle_waiting_sessions = paginator_oracle_waiting_session.page(page_oracle_waiting_session)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        oracle_waiting_sessions = paginator_oracle_waiting_session.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        oracle_waiting_sessions = paginator_oracle_waiting_session.page(page_oracle_waiting_session.num_pages)
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
    return render_to_response('oracle_waiting_session.html',
                              {'messageinfo_list': messageinfo_list,'oracle_waiting_sessions':oracle_waiting_sessions,
                               'tags': tags,
                               'msg_num': msg_num, 'now': now,
                               'msg_last_content': msg_last_content, 'tim_last': tim_last})

@login_required(login_url='/login')
def oracle_pga(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    tags = request.GET.get('tags')
    sql = "select host,port,service_name,user,password,user_os,password_os from tab_oracle_servers where tags= '%s' " % tags
    oracle = tools.mysql_query(sql)
    host = oracle[0][0]
    port = oracle[0][1]
    service_name = oracle[0][2]
    user = oracle[0][3]
    password = oracle[0][4]
    password = base64.decodestring(password)
    url = host + ':' + port + '/' + service_name
    # session temp
    sql_pga = '''select b.program,
       b.status,
       b.username,
       b.MACHINE,b.osuser,
       b.LOGON_TIME,
       a.spid,
       a.PGA_USED_MEM,
       a.PGA_ALLOC_MEM,
       a.PGA_FREEABLE_MEM,
       a.PGA_MAX_MEM
  from v$process a, v$session b
 where a.addr = b.PADDR '''

    oracle_pgas = tools.oracle_django_query(user, password, url, sql_pga)
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
    return render_to_response('oracle_pga.html',
                              {'messageinfo_list': messageinfo_list,'oracle_pgas':oracle_pgas,
                               'tags': tags,
                               'msg_num': msg_num, 'now': now,
                               'msg_last_content': msg_last_content, 'tim_last': tim_last})

@login_required(login_url='/login')
def oracle_para(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    tags = request.GET.get('tags')
    sql = "select host,port,service_name,user,password,user_os,password_os from tab_oracle_servers where tags= '%s' " % tags
    oracle = tools.mysql_query(sql)
    host = oracle[0][0]
    port = oracle[0][1]
    service_name = oracle[0][2]
    user = oracle[0][3]
    password = oracle[0][4]
    password = base64.decodestring(password)
    url = host + ':' + port + '/' + service_name
    # 基础信息
    sql_db = "select NAME,CREATED,LOG_MODE,OPEN_MODE,PROTECTION_MODE,DATABASE_ROLE,PLATFORM_NAME,CURRENT_SCN,FLASHBACK_ON from v$database"
    dbinfos = tools.oracle_django_query(user,password,url,sql_db)
    sql_instance = "select instance_number,instance_name,host_name,version,startup_time,status,instance_role from v$instance"
    instanceinfos = tools.oracle_django_query(user,password,url,sql_instance)
    db_domain = ora_do.get_oracle_para(url,user,password,'db_domain')
    service_names = ora_do.get_oracle_para(url,user,password,'service_names')

    # 字符集
    sql_charset = "select userenv('language') charset from dual"
    charsets = tools.oracle_django_query(user,password,url,sql_charset)
    # 连接相关参数
    p_processes = ora_do.get_oracle_para(url,user,password,'processes')
    p_sessions = ora_do.get_oracle_para(url,user,password,'sessions')

    # undo相关参数
    undo_tablespace = ora_do.get_oracle_para(url,user,password,'undo_tablespace')
    undo_management = ora_do.get_oracle_para(url,user,password,'undo_management')
    undo_retention = ora_do.get_oracle_para(url,user,password,'undo_retention')

    # 内存设置相关
    memory_target = ora_do.get_oracle_para(url,user,password,'memory_target')
    memory_target = int(memory_target)/1024/1024
    memory_max_target = ora_do.get_oracle_para(url,user,password,'memory_max_target')
    memory_max_target = int(memory_max_target)/1024/1024
    sga_target = ora_do.get_oracle_para(url,user,password,'sga_target')
    sga_target = int(sga_target)/1024/1024
    pga_aggregate_target = ora_do.get_oracle_para(url,user,password,'pga_aggregate_target')
    pga_aggregate_target = int(pga_aggregate_target)/1024/1024
    sga_max_size = ora_do.get_oracle_para(url,user,password,'sga_max_size')
    sga_max_size = int(sga_max_size)/1024/1024
    shared_pool_size = ora_do.get_oracle_para(url,user,password,'shared_pool_size')
    shared_pool_size = int(shared_pool_size)/1024/1024
    db_cache_size = ora_do.get_oracle_para(url, user, password, 'db_cache_size')
    db_cache_size = int(db_cache_size)/1024/1024
    shared_pool_reserved_size = ora_do.get_oracle_para(url, user, password, 'shared_pool_reserved_size')
    shared_pool_reserved_size = int(shared_pool_reserved_size)/1024/1024

    # 其他参数
    db_files = ora_do.get_oracle_para(url,user,password,'db_files')
    lock_sga = ora_do.get_oracle_para(url,user,password,'lock_sga')
    parallel_force_local = ora_do.get_oracle_para(url,user,password,'parallel_force_local')
    cursor_sharing = ora_do.get_oracle_para(url,user,password,'cursor_sharing')
    open_cursors = ora_do.get_oracle_para(url,user,password,'open_cursors')
    session_cached_cursors = ora_do.get_oracle_para(url,user,password,'session_cached_cursors')
    log_checkpoints_to_alert = ora_do.get_oracle_para(url,user,password,'log_checkpoints_to_alert')
    log_checkpoint_timeout = ora_do.get_oracle_para(url,user,password,'log_checkpoint_timeout')
    resource_limit = ora_do.get_oracle_para(url,user,password,'resource_limit')
    parallel_max_servers = ora_do.get_oracle_para(url,user,password,'parallel_max_servers')
    parallel_servers_target = ora_do.get_oracle_para(url,user,password,'parallel_servers_target')

    # DATAGUARD相关
    log_archive_dest_1 = ora_do.get_oracle_para(url,user,password,'log_archive_dest_1')
    log_archive_dest_2 = ora_do.get_oracle_para(url,user,password,'log_archive_dest_2')
    log_archive_dest_state_1 = ora_do.get_oracle_para(url,user,password,'log_archive_dest_state_1')
    log_archive_dest_state_2 = ora_do.get_oracle_para(url,user,password,'log_archive_dest_state_2')
    standby_file_management = ora_do.get_oracle_para(url,user,password,'standby_file_management')
    fal_server = ora_do.get_oracle_para(url,user,password,'fal_server')
    fal_client = ora_do.get_oracle_para(url,user,password,'fal_client')
    db_file_name_convert = ora_do.get_oracle_para(url,user,password,'db_file_name_convert')
    log_file_name_convert = ora_do.get_oracle_para(url,user,password,'log_file_name_convert')
    dg_broker_start = ora_do.get_oracle_para(url,user,password,'dg_broker_start')

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
    return render_to_response('oracle_para.html',
                              {'messageinfo_list': messageinfo_list,'p_processes':p_processes,'p_sessions':p_sessions,
                               'tags': tags,'dbinfos':dbinfos,'instanceinfos':instanceinfos,'charsets':charsets,'db_domain':db_domain,'service_names':service_names,
                               'undo_tablespace':undo_tablespace,'undo_management':undo_management,
                               'undo_retention':undo_retention,'memory_target':memory_target,'memory_max_target':memory_max_target,
                               'sga_target':sga_target,'sga_max_size':sga_max_size,'pga_aggregate_target':pga_aggregate_target,'shared_pool_size':shared_pool_size,
                               'shared_pool_reserved_size':shared_pool_reserved_size,'db_cache_size':db_cache_size,
                               'db_files':db_files,'lock_sga':lock_sga,'parallel_force_local':parallel_force_local,'cursor_sharing':cursor_sharing,
                               'open_cursors':open_cursors,'session_cached_cursors':session_cached_cursors,'log_checkpoints_to_alert':log_checkpoints_to_alert,
                               'log_checkpoint_timeout':log_checkpoint_timeout,'resource_limit':resource_limit,'parallel_max_servers':parallel_max_servers,
                               'parallel_servers_target':parallel_servers_target,
                               'log_archive_dest_1':log_archive_dest_1,'log_archive_dest_2':log_archive_dest_2,'log_archive_dest_state_1':log_archive_dest_state_1,
                               'log_archive_dest_state_2':log_archive_dest_state_2,'standby_file_management':standby_file_management,'fal_server':fal_server,
                               'fal_client':fal_client,'db_file_name_convert':db_file_name_convert,'log_file_name_convert':log_file_name_convert,
                               'msg_num': msg_num, 'now': now,
                               'msg_last_content': msg_last_content, 'tim_last': tim_last})

@login_required(login_url='/login')
def oracle_switchover(request):
    # 告警
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()

    primary_tags = request.GET.get('primary_tags')
    primary_curr_role = request.GET.get('primary_curr_role')
    standby_tags = request.GET.get('standby_tags')
    standby_curr_role = request.GET.get('standby_curr_role')
    if primary_tags:
        if not primary_curr_role == 'PRIMARY':
            p_tags = standby_tags
            s_tags = primary_tags
        else:
            p_tags = primary_tags
            s_tags = standby_tags
        p_sql = "select host,port,service_name,user,password,user_os,password_os from tab_oracle_servers where tags= '%s' " % p_tags
        p_ssh = tools.mysql_query(p_sql)
        p_host = p_ssh[0][0]
        p_user = p_ssh[0][5]
        p_password = p_ssh[0][6]
        p_password = base64.decodestring(p_password)
        s_sql = "select host,port,service_name,user,password,user_os,password_os from tab_oracle_servers where tags= '%s' " % s_tags
        s_ssh = tools.mysql_query(s_sql)
        s_host = s_ssh[0][0]
        s_user = s_ssh[0][5]
        s_password = s_ssh[0][6]
        s_password = base64.decodestring(s_password)
        task.oracle_switchover.delay(p_tags,p_host,p_user,p_password,s_tags,s_host,s_user,s_password)
        messages.add_message(request,messages.INFO,'正在切换')


    oracle_switchover_list = models_oracle.OracleSwitchover.objects.all()
    paginator_oracle_switchover = Paginator(oracle_switchover_list, 5)
    page_oracle_switchover = request.GET.get('page_oracle_switchover')
    try:
        oracle_switchovers = paginator_oracle_switchover.page(page_oracle_switchover)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        oracle_switchovers = paginator_oracle_switchover.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        oracle_switchovers = paginator_oracle_switchover.page(page_oracle_switchover.num_pages)
    now = tools.now()
    sql_refresh = 'update oracle_switchover t1 set t1.primary_curr_role = (select database_role from oracle_db where tags=t1.primary_tags),t1.adg_trans_lag =(select adg_transport_lag from oracle_db where tags=t1.primary_tags),t1.adg_apply_lag=(select adg_apply_lag from oracle_db where tags=t1.primary_tags)'
    tools.mysql_exec(sql_refresh,'')
    sql_refresh = 'update oracle_switchover t1 set t1.standby_curr_role = (select database_role from oracle_db where tags=t1.standby_tags),t1.adg_trans_lag =(select ifnull(t1.adg_trans_lag,adg_transport_lag) from oracle_db where tags=t1.standby_tags),t1.adg_apply_lag=(select ifnull(t1.adg_apply_lag,adg_apply_lag) from oracle_db where tags=t1.standby_tags)'
    tools.mysql_exec(sql_refresh,'')


    log_type = 'Oracle容灾切换'
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
    return render(request,'oracle_switchover.html',
                              {'messageinfo_list': messageinfo_list, 'oracle_switchovers': oracle_switchovers, 'log_type': log_type, 'now': now,'msg_num':msg_num,
                               'msg_last_content': msg_last_content, 'tim_last': tim_last})

@login_required(login_url='/login')
def oracle_top_sql(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    tagsinfo = models_oracle.TabOracleServers.objects.all().order_by('tags')

    tagsdefault = request.GET.get('tagsdefault')
    if not tagsdefault:
        tagsdefault = models_oracle.TabOracleServers.objects.order_by('tags')[0].tags
    sql = "select host,port,service_name,user,password,user_os,password_os from tab_oracle_servers where tags= '%s' " % tagsdefault
    oracle = tools.mysql_query(sql)
    host = oracle[0][0]
    port = oracle[0][1]
    service_name = oracle[0][2]
    user = oracle[0][3]
    password = oracle[0][4]
    password = base64.decodestring(password)
    url = host + ':' + port + '/' + service_name
    # 执行top cpu sql生成存储过程
    tools.oracle_call_proc(user, password, url, 'pro_top_cpu_sql')
    # 查询配置
    sql_cpu_config = '''select * from snap_show_config where id=1'''
    cpu_sql_configs = tools.oracle_django_query(user, password, url, sql_cpu_config)
    # 查询快照数据
    sql_cpu = '''select * from snap_show where snap_type_id=1 order by id '''
    cpu_sqls = tools.oracle_django_query(user, password, url, sql_cpu)

    # 执行top logic sql生成存储过程
    tools.oracle_call_proc(user,password,url,'pro_top_logic_sql')
    # 查询配置
    sql_logic_config = '''select * from snap_show_config where id=2'''
    logic_sql_configs = tools.oracle_django_query(user, password, url, sql_logic_config)
    # 查询快照数据
    sql_logic = '''select * from snap_show where snap_type_id=2 order by id '''
    logic_sqls = tools.oracle_django_query(user, password, url, sql_logic)

    # 执行top phys sql生成存储过程
    tools.oracle_call_proc(user,password,url,'pro_top_phys_sql')
    # 查询配置
    sql_phys_config = '''select * from snap_show_config where id=3'''
    phys_sql_configs = tools.oracle_django_query(user, password, url, sql_phys_config)
    # 查询快照数据
    sql_phys = '''select * from snap_show where snap_type_id=3 order by id '''
    phys_sqls = tools.oracle_django_query(user, password, url, sql_phys)

    if request.method == 'POST':
        if request.POST.has_key('select_tags') :
            tagsdefault = request.POST.get('select_tags', None).encode("utf-8")
            return HttpResponseRedirect('/oracle_top_sql?tagsdefault=%s' %(tagsdefault))
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
    return render_to_response('oracle_top_sql.html', {'tagsdefault': tagsdefault, 'tagsinfo': tagsinfo,'msg_num':msg_num,
                                                      'msg_last_content': msg_last_content, 'tim_last': tim_last,
                                                      'cpu_sql_configs': cpu_sql_configs, 'cpu_sqls': cpu_sqls,
                                                      'logic_sql_configs':logic_sql_configs,'logic_sqls':logic_sqls,
                                                      'phys_sql_configs': phys_sql_configs, 'phys_sqls': phys_sqls})

@login_required(login_url='/login')
def oracle_sql(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    tags = request.GET.get('tags')
    sql_id = request.GET.get('sql_id')
    sql = "select host,port,service_name,user,password,user_os,password_os from tab_oracle_servers where tags= '%s' " %tags
    oracle = tools.mysql_query(sql)
    host = oracle[0][0]
    port = oracle[0][1]
    service_name = oracle[0][2]
    user = oracle[0][3]
    password = oracle[0][4]
    password = base64.decodestring(password)
    url = host + ':' + port + '/' + service_name
    sql = '''SELECT SQL_TEXT FROM V$SQLTEXT WHERE SQL_ID = to_char('%s') ORDER BY PIECE''' %sql_id
    sql_texts = tools.oracle_django_query(user,password,url,sql)
    sql_plan = '''SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(to_char('%s'),NULL))''' %sql_id
    sql_plans = tools.oracle_django_query(user,password,url,sql_plan)

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
    return render_to_response('oracle_sql.html',
                              {'messageinfo_list': messageinfo_list,'sql_id':sql_id, 'sql_texts': sql_texts,'sql_plans':sql_plans, 'tags': tags,
                               'now': now,'msg_num':msg_num,
                               'msg_last_content': msg_last_content, 'tim_last': tim_last})


@login_required(login_url='/login')
def oracle_backup(request):
    backup_set = request.GET.get('backup_set')
    backup_piece = request.GET.get('backup_piece')

    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    now = tools.now()

    # 收集oracle备份数据
    oracle_backupinfo.do_collect()
    if backup_set:
        oracle_backups = models_oracle.OracleBackupInfo.objects.filter(tags=backup_set)
    else:
        oracle_backups = models_oracle.OracleBackupInfo.objects.all().order_by('id')
    if backup_piece:
        oracle_backup_pieces = models_oracle.OracleBackupPiece.objects.filter(tags=backup_piece)
    else:
        oracle_backup_pieces = models_oracle.OracleBackupPiece.objects.all().order_by('id')

    # 加载Oracle备份任务
    oracle_bak_job = '''select t1.job_no,t1.job_name,t1.tags,t1.bak_conf_no,t1.bak_conf_name,t2.bak_type,
     (case t1.is_on when 1 then 'on' else 'off' end) is_on,
     (case t1.is_on when 1 then 'green' else 'red' end) is_on1,t1.next_bak_time from oracle_bak_job t1 left join bak_conf t2 on t1.bak_conf_no=t2.conf_no '''
    oracle_bak_jobs = tools.mysql_django_query( oracle_bak_job)

    if request.method == 'POST':
        if request.POST.has_key('backup_set'):
            backup_set = request.POST.get('backup_set').encode("utf-8")
            return HttpResponseRedirect('/oracle_backup?backup_set=%s' % (backup_set))
        elif request.POST.has_key('backup_piece'):
            backup_piece = request.POST.get('backup_piece').encode("utf-8")
            return HttpResponseRedirect('/oracle_backup?backup_piece=%s' % ( backup_piece))
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
    return render_to_response('oracle_backup.html', {'messageinfo_list': messageinfo_list,'msg_num':msg_num,'msg_last_content':msg_last_content,'tim_last':tim_last,
                                                   'now': now,'oracle_backups':oracle_backups,'oracle_backup_pieces':oracle_backup_pieces,'oracle_bak_jobs':oracle_bak_jobs})

@login_required(login_url='/login')
def oracle_rpt(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    tagsinfo = models_oracle.TabOracleServers.objects.all()

    tagsdefault = request.GET.get('tagsdefault')
    if not tagsdefault:
        tagsdefault = models_oracle.TabOracleServers.objects.order_by('tags')[0].tags
    typedefault = request.GET.get('typedefault')
    if not typedefault:
        typedefault = '生成AWR报告'
    if typedefault == unicode('生成AWR报告', 'utf-8'):
        report_type = 'awr'
    elif typedefault == unicode('生成ASH报告', 'utf-8'):
        report_type = 'ash'
    else:
        report_type = 'addm'

    db_range_default = request.GET.get('db_range_default')

    if not db_range_default:
        db_range_default = '1小时'.decode("utf-8")

    db_begin_time = tools.range(db_range_default)
    end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    dbgrow = models_oracle.OracleDbHis.objects.filter(tags=tagsdefault, dbtime__isnull=False).filter(
        chk_time__gt=db_begin_time, chk_time__lt=end_time).order_by('-chk_time')
    dbgrow_list = list(dbgrow)
    dbgrow_list.reverse()

    # 获取快照
    snap_range = tools.snap_range(db_range_default)
    sql = "select host,port,service_name,user,password,user_os,password_os from tab_oracle_servers where tags= '%s' " % tagsdefault
    oracle = tools.mysql_query(sql)
    host = oracle[0][0]
    port = oracle[0][1]
    service_name = oracle[0][2]
    user = oracle[0][3]
    password = oracle[0][4]
    password = base64.decodestring(password)
    url = host + ':' + port + '/' + service_name
    sql = """
           SELECT dbid,
              to_char(s.startup_time, 'yyyy-mm-dd hh24:mi:ss') snap_startup_time,
              to_char(s.begin_interval_time,
                      'yyyy-mm-dd hh24:mi:ss') begin_interval_time,
              to_char(s.end_interval_time, 'yyyy-mm-dd hh24:mi:ss') end_interval_time,
              s.snap_id, s.instance_number,
              (cast(s.end_interval_time as date) - cast(s.begin_interval_time as date))*86400 as span_in_second
           from dba_hist_snapshot  s, v$instance b
           where s.end_interval_time >= sysdate - %s/24
           and s.INSTANCE_NUMBER = b.INSTANCE_NUMBER order by snap_id
       """ %snap_range
    oracle_snap_shots = tools.oracle_django_query(user,password,url,sql)
    # 报告列表
    oracle_reports = models_oracle.OracleReport.objects.filter(tags=tagsdefault).order_by('id')

    begin_time = (datetime.datetime.now() + datetime.timedelta(hours=-1)).strftime("%Y%m%d %H:%M:%S")
    end_time = datetime.datetime.now().strftime("%Y%m%d %H:%M:%S")

    if request.method == 'POST':
        if request.POST.has_key('select_tags') :
            tagsdefault = request.POST.get('select_tags', None).encode("utf-8")
            return HttpResponseRedirect('/oracle_rpt?tagsdefault=%s&typedefault=%s&db_range_default=%s' %(tagsdefault,typedefault,db_range_default))
        elif request.POST.has_key('select_type'):
            typedefault = request.POST.get('select_type', None).encode("utf-8")
            if typedefault == '生成ASH报告':
                return HttpResponseRedirect('/oracle_rpt_ash?tagsdefault=%s&typedefault=%s&db_range_default=%s' % (
                tagsdefault, typedefault, db_range_default))
            else:
                return HttpResponseRedirect('/oracle_rpt?tagsdefault=%s&typedefault=%s&db_range_default=%s' % (
                tagsdefault, typedefault, db_range_default))
        elif request.POST.has_key('commit'):
            begin_snap = request.POST.get('begin_snap', None)
            end_snap = request.POST.get('end_snap', None)
            task.get_report.delay(tagsdefault,url,user,password,report_type,begin_snap,end_snap)
            messages.add_message(request, messages.SUCCESS, '正在生成')

        elif request.POST.has_key('commit_event'):
            begin_time = request.POST.get('begin_time', None)
            end_time = request.POST.get('end_time', None)
            begin_time = datetime.datetime.strptime(begin_time, '%Y-%m-%dT%H:%M').strftime("%Y%m%d %H:%M:%S")
            end_time = datetime.datetime.strptime(end_time, '%Y-%m-%dT%H:%M').strftime("%Y%m%d %H:%M:%S")
        else:
            logout(request)
            return HttpResponseRedirect('/login/')


    sql = ''' SELECT *
               FROM (SELECT a.program,
               a.sql_id,
               a.session_state,
               a.event,
               count(*) cnt,
               lpad(round(ratio_to_report(count(*)) over() * 100) || '%%',
                    10,
                    ' ') percent,
               MIN(a.sample_time) min_tim,
               MAX(a.sample_time) max_tim
          FROM dba_hist_active_sess_history a
         WHERE a.sample_time BETWEEN
               to_date('%s','YYYYMMDD HH24:MI:SS') AND
               to_date('%s','YYYYMMDD HH24:MI:SS')
         GROUP BY a.program, a.sql_id, a.session_state, a.event
         ORDER BY percent DESC)
     WHERE ROWNUM <= 30 ''' %(begin_time,end_time)
    oracle_events = tools.oracle_django_query(user,password,url,sql)

    if messageinfo_list:
        msg_num = len(messageinfo_list)
        msg_last = models_frame.TabAlarmInfo.objects.latest('id')
        msg_last_content = msg_last.alarm_content
        tim_last = (datetime.datetime.now() - msg_last.alarm_time).seconds / 60
    else:
        msg_num = 0
        msg_last_content = ''
        tim_last = ''
    return render(request,'oracle_rpt.html', {'tagsdefault': tagsdefault,'typedefault':typedefault,'tagsinfo': tagsinfo,'msg_num':msg_num,
                                                      'msg_last_content': msg_last_content, 'tim_last': tim_last,'dbgrow_list':dbgrow_list,
                                                  'oracle_snap_shots':oracle_snap_shots,'oracle_reports':oracle_reports,
                                                  'oracle_events':oracle_events})

@login_required(login_url='/login')
def oracle_rpt_ash(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    tagsinfo = models_oracle.TabOracleServers.objects.all()

    tagsdefault = request.GET.get('tagsdefault')
    if not tagsdefault:
        tagsdefault = models_oracle.TabOracleServers.objects.order_by('tags')[0].tags
    typedefault = request.GET.get('typedefault')
    if not typedefault:
        typedefault = '生成AWR报告'
    if typedefault == unicode('生成AWR报告', 'utf-8'):
        report_type = 'awr'
    elif typedefault == unicode('生成ASH报告', 'utf-8'):
        report_type = 'ash'
    else:
        report_type = 'addm'

    db_range_default = request.GET.get('db_range_default')

    if not db_range_default:
        db_range_default = '1小时'.decode("utf-8")

    db_begin_time = tools.range(db_range_default)

    end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    dbgrow = models_oracle.OracleDbHis.objects.filter(tags=tagsdefault, dbtime__isnull=False).filter(
        chk_time__gt=db_begin_time, chk_time__lt=end_time).order_by('-chk_time')
    dbgrow_list = list(dbgrow)
    dbgrow_list.reverse()

    # 获取快照
    snap_range = tools.snap_range(db_range_default)
    sql = "select host,port,service_name,user,password,user_os,password_os from tab_oracle_servers where tags= '%s' " % tagsdefault
    oracle = tools.mysql_query(sql)
    host = oracle[0][0]
    port = oracle[0][1]
    service_name = oracle[0][2]
    user = oracle[0][3]
    password = oracle[0][4]
    password = base64.decodestring(password)
    url = host + ':' + port + '/' + service_name
    sql = """
           SELECT dbid,
              to_char(s.startup_time, 'yyyy-mm-dd hh24:mi:ss') snap_startup_time,
              to_char(s.begin_interval_time,
                      'yyyy-mm-dd hh24:mi:ss') begin_interval_time,
              to_char(s.end_interval_time, 'yyyy-mm-dd hh24:mi:ss') end_interval_time,
              s.snap_id, s.instance_number,
              (cast(s.end_interval_time as date) - cast(s.begin_interval_time as date))*86400 as span_in_second
           from dba_hist_snapshot  s, v$instance b
           where s.end_interval_time >= sysdate - %s/24
           and s.INSTANCE_NUMBER = b.INSTANCE_NUMBER order by snap_id
       """ %snap_range
    oracle_snap_shots = tools.oracle_django_query(user,password,url,sql)
    # 报告列表
    oracle_reports = models_oracle.OracleReport.objects.filter(tags=tagsdefault).order_by('id')

    begin_time = (datetime.datetime.now() + datetime.timedelta(hours=-1)).strftime("%Y%m%d %H:%M:%S")
    end_time = datetime.datetime.now().strftime("%Y%m%d %H:%M:%S")


    if request.method == 'POST':
        if request.POST.has_key('select_tags') :
            tagsdefault = request.POST.get('select_tags', None).encode("utf-8")
            return HttpResponseRedirect('/oracle_rpt?tagsdefault=%s&typedefault=%s&db_range_default=%s' %(tagsdefault,typedefault,db_range_default))
        elif request.POST.has_key('select_type'):
            typedefault = request.POST.get('select_type', None).encode("utf-8")
            if typedefault == '生成ASH报告':
                return HttpResponseRedirect('/oracle_rpt_ash?tagsdefault=%s&typedefault=%s&db_range_default=%s' % (
                tagsdefault, typedefault, db_range_default))
            else:
                return HttpResponseRedirect('/oracle_rpt?tagsdefault=%s&typedefault=%s&db_range_default=%s' % (
                tagsdefault, typedefault, db_range_default))
        elif request.POST.has_key('commit'):
            begin_snap = request.POST.get('begin_snap', None)
            end_snap = request.POST.get('end_snap', None)
            task.get_report.delay(tagsdefault,url,user,password,report_type,begin_snap,end_snap)
        elif request.POST.has_key('commit_event'):
            begin_time = request.POST.get('begin_time', None)
            end_time = request.POST.get('end_time', None)
            begin_time = datetime.datetime.strptime(begin_time, '%Y-%m-%dT%H:%M').strftime("%Y%m%d %H:%M:%S")
            end_time = datetime.datetime.strptime(end_time, '%Y-%m-%dT%H:%M').strftime("%Y%m%d %H:%M:%S")
        else:
            logout(request)
            return HttpResponseRedirect('/login/')

    sql = ''' SELECT *
                 FROM (SELECT a.program,
                 a.sql_id,
                 a.session_state,
                 a.event,
                 count(*) cnt,
                 lpad(round(ratio_to_report(count(*)) over() * 100) || '%%',
                      10,
                      ' ') percent,
                 MIN(a.sample_time) min_tim,
                 MAX(a.sample_time) max_tim
            FROM dba_hist_active_sess_history a
           WHERE a.sample_time BETWEEN
                 to_date('%s','YYYYMMDD HH24:MI:SS') AND
                 to_date('%s','YYYYMMDD HH24:MI:SS')
           GROUP BY a.program, a.sql_id, a.session_state, a.event
           ORDER BY percent DESC)
       WHERE ROWNUM <= 30 ''' % (begin_time, end_time)
    oracle_events = tools.oracle_django_query(user, password, url, sql)

    if messageinfo_list:
        msg_num = len(messageinfo_list)
        msg_last = models_frame.TabAlarmInfo.objects.latest('id')
        msg_last_content = msg_last.alarm_content
        tim_last = (datetime.datetime.now() - msg_last.alarm_time).seconds / 60
    else:
        msg_num = 0
        msg_last_content = ''
        tim_last = ''
    return render_to_response('oracle_rpt_ash.html', {'tagsdefault': tagsdefault,'typedefault':typedefault,'tagsinfo': tagsinfo,'msg_num':msg_num,
                                                      'msg_last_content': msg_last_content, 'tim_last': tim_last,'dbgrow_list':dbgrow_list,
                                                  'oracle_snap_shots':oracle_snap_shots,'oracle_reports':oracle_reports,
                                                      'oracle_events':oracle_events})



@login_required(login_url='/login')
def show_report(request):
    report_path = request.GET.get('report_path')
    if 'txt' in report_path:
        local_file = os.getcwd() + '/templates/' + report_path
        txt_data = open(local_file, "rb")
        list = txt_data.xreadlines()
        return render_to_response('show_txt.html',{'aList':list})
    else:
        return render_to_response(report_path)

@login_required(login_url='/login')
def delete_report(request):
    report_path = request.GET.get('report_path')
    id = request.GET.get('id')
    local_path = os.getcwd() + '/templates/' + report_path
    os.remove(local_path)
    sql = 'delete from oracle_report where id=%s' %id
    tools.mysql_exec(sql,'')
    return HttpResponseRedirect('/oracle_rpt/')

@login_required(login_url='/login')
def oracle_tbs(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()

    tags = request.GET.get('tags')
    tbs_name = request.GET.get('tbs_name')

    db_range_default = request.GET.get('db_range_default')

    if not db_range_default:
        db_range_default = '1小时'.decode("utf-8")

    db_begin_time = tools.range(db_range_default)

    end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    tbsgrow = models_oracle.OracleTbsHis.objects.filter(tags=tags,tbs_name=tbs_name,used_gb__isnull=False).filter(
        chk_time__gt=db_begin_time, chk_time__lt=end_time).order_by('-chk_time')
    tbsgrow_list = list(tbsgrow)
    tbsgrow_list.reverse()
    if tbsgrow:
        tbsgrow_max = models_oracle.OracleTbsHis.objects.filter(tags=tags, tbs_name=tbs_name,used_gb__isnull=False).filter(
            chk_time__gt=db_begin_time, chk_time__lt=end_time).order_by('-used_gb')[0]
        max_tbs_used =  tbsgrow_max.used_gb
    else:
        max_tbs_used = 0

    # 获取段对象
    sql = "select host,port,service_name,user,password,user_os,password_os from tab_oracle_servers where tags= '%s' " % tags
    oracle = tools.mysql_query(sql)
    host = oracle[0][0]
    port = oracle[0][1]
    service_name = oracle[0][2]
    user = oracle[0][3]
    password = oracle[0][4]
    password = base64.decodestring(password)
    url = host + ':' + port + '/' + service_name
    sql = """select owner, segment_name,partition_name,segment_type, sum(bytes) / 1024 / 1024 / 1024 gbytes
             from dba_segments
            where tablespace_name = '%s'
             group by owner, segment_name,partition_name,segment_type
            having sum(bytes) / 1024 / 1024/1024 > 0.05
          order by 3 desc
       """ %tbs_name
    oracle_tbs_segments = tools.oracle_django_query(user,password,url,sql)
    sql = '''select trunc(to_date(rtime, 'mm/dd/yyyy hh24:mi:ss'), 'dd') m_date,
              round(sum(tablespace_usedsize) / 1024 / 1024) used_mb
            from dba_hist_tbspc_space_usage a, v$tablespace b
           where a.tablespace_id = b.ts#
            and b.name = 'SYSAUX'
           group by trunc(to_date(rtime, 'mm/dd/yyyy hh24:mi:ss'), 'dd')
            order by 1'''
    oracle_pers = tools.oracle_django_query(user,password,url,sql)

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
    return render_to_response('oracle_tbs.html', {'tags': tags,'tbs_name':tbs_name,'msg_num':msg_num,
                                                      'msg_last_content': msg_last_content, 'tim_last': tim_last,'tbsgrow_list':tbsgrow_list,
                                                  'oracle_tbs_segments':oracle_tbs_segments,'oracle_pers':oracle_pers,'max_tbs_used':max_tbs_used})


def my_task(request):
    # 告警
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()

    # 数据库操作面板
    my_task_sql = '''select t1.task_id,
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
          from my_task t1 order by start_time desc '''

    my_task_list = tools.mysql_django_query(my_task_sql)

    paginator_my_task = Paginator(my_task_list, 10)
    page_my_task = request.GET.get('page')
    try:
        my_tasks = paginator_my_task.page(page_my_task)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        my_tasks = paginator_my_task.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        my_tasks = paginator_my_task.page(paginator_my_task.num_pages)

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
    return render(request,'my_task.html',
                              {'messageinfo_list': messageinfo_list, 'my_tasks': my_tasks,
                               'msg_num': msg_num, 'now': now,
                               'msg_last_content': msg_last_content, 'tim_last': tim_last}
                              )


@login_required(login_url='/login')
def oracle_perf(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    tagsinfo = models_oracle.TabOracleServers.objects.all()

    tagsdefault = request.GET.get('tagsdefault')
    if not tagsdefault:
        tagsdefault = models_oracle.TabOracleServers.objects.order_by('tags')[0].tags

    db_range_default = request.GET.get('db_range_default')

    if not db_range_default:
        db_range_default = '1小时'.decode("utf-8")

    db_begin_time = tools.range(db_range_default)
    end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    dbgrow = models_oracle.OracleDbHis.objects.filter(tags=tagsdefault, dbtime__isnull=False).filter(
        chk_time__gt=db_begin_time, chk_time__lt=end_time).order_by('-chk_time')
    dbgrow_list = list(dbgrow)
    dbgrow_list.reverse()


    if request.method == 'POST':
        if request.POST.has_key('select_tags') :
            tagsdefault = request.POST.get('select_tags', None).encode("utf-8")
            return HttpResponseRedirect('/oracle_perf?tagsdefault=%s&db_range_default=%s' %(tagsdefault,db_range_default))
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
    return render(request,'oracle_perf.html', {'tagsdefault': tagsdefault,'tagsinfo': tagsinfo,'msg_num':msg_num,
                                                'msg_last_content': msg_last_content, 'tim_last': tim_last,
                                               'dbgrow_list':dbgrow_list})
