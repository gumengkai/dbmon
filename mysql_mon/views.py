#! /usr/bin/python
# encoding:utf-8

from django.shortcuts import render

from django.shortcuts import render,render_to_response
from django.http import HttpResponse, HttpResponseRedirect

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# Create your views here.
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from django.http import HttpResponse
import datetime
from frame import tools
# 配置文件
import ConfigParser
import base64
import frame.models as models_frame
import linux_mon.models as models_linux
import oracle_mon.models as models_oracle
import mysql_mon.models as models_mysql
import frame.tools as tools
import MySQLdb
import check_alarm.check_mysql as check_msql
import frame.log_parse as logparser
import tasks as task
from django.contrib import messages
import paramiko

# Create your views here.


@login_required(login_url='/login')
def mysql_monitor(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    tagsinfo = models_mysql.TabMysqlServers.objects.all().order_by('tags')

    tagsdefault = request.GET.get('tagsdefault')
    if not tagsdefault:
        tagsdefault = models_mysql.TabMysqlServers.objects.order_by('tags')[0].tags

    conn_range_default = request.GET.get('conn_range_default')
    if not conn_range_default:
        conn_range_default = '1小时'.decode("utf-8")

    ps_range_default = request.GET.get('ps_range_default')
    if not ps_range_default:
        ps_range_default = '1小时'.decode("utf-8")

    thread_range_default = request.GET.get('thread_range_default')
    if not thread_range_default:
        thread_range_default = '1小时'.decode("utf-8")

    net_range_default = request.GET.get('net_range_default')
    if not net_range_default:
        net_range_default = '1小时'.decode("utf-8")

    conn_begin_time = tools.range(conn_range_default)
    ps_begin_time = tools.range(ps_range_default)
    thread_begin_time = tools.range(thread_range_default)
    net_begin_time = tools.range(net_range_default)

    end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # 取最近一次采集数据
    try:
        mysql_curr = models_mysql.MysqlDb.objects.get(tags=tagsdefault)
    except models_mysql.MysqlDb.DoesNotExist:
        mysql_curr = \
            models_mysql.MysqlDbHis.objects.filter(tags=tagsdefault).order_by('-chk_time')[
                0]
    # 取最近一次采集正常数据
    try:
        try:
            mysqlinfo = models_mysql.MysqlDb.objects.get(tags=tagsdefault,version__isnull=False)
        except models_mysql.MysqlDb.DoesNotExist:
            mysqlinfo = \
                models_mysql.MysqlDbHis.objects.filter(tags=tagsdefault, version__isnull=False).order_by('-chk_time')[
                    0]
    except Exception, e:
        mysqlinfo = \
            models_mysql.MysqlDbHis.objects.filter(tags=tagsdefault).order_by('-chk_time')[
                0]

    if mysql_curr.mon_status == 'connected':
        check_status = 'success'
        mysql_status = '在线'
    else:
        check_status = 'danger'
        mysql_status = '离线'

    conngrow = models_mysql.MysqlDbHis.objects.filter(tags=tagsdefault, conn_rate__isnull=False).filter(
        chk_time__gt=conn_begin_time, chk_time__lt=end_time).order_by('-chk_time')
    conngrow_list = list(conngrow)
    conngrow_list.reverse()
    qpsgrow = models_mysql.MysqlDbHis.objects.filter(tags=tagsdefault, qps__isnull=False).filter(
        chk_time__gt=ps_begin_time, chk_time__lt=end_time).order_by('-chk_time')
    qpsgrow_list = list(qpsgrow)
    qpsgrow_list.reverse()

    tpsgrow = models_mysql.MysqlDbHis.objects.filter(tags=tagsdefault, tps__isnull=False).filter(
        chk_time__gt=ps_begin_time, chk_time__lt=end_time).order_by('-chk_time')
    tpsgrow_list = list(tpsgrow)
    tpsgrow_list.reverse()

    threadgrow = models_mysql.MysqlDbHis.objects.filter(tags=tagsdefault, threads_cached__isnull=False).filter(
        chk_time__gt=thread_begin_time, chk_time__lt=end_time).order_by('-chk_time')
    threadgrow_list = list(threadgrow)
    threadgrow_list.reverse()

    netgrow = models_mysql.MysqlDbHis.objects.filter(tags=tagsdefault, bytes_received__isnull=False).filter(
        chk_time__gt=net_begin_time, chk_time__lt=end_time).order_by('-chk_time')
    netgrow_list = list(netgrow)
    netgrow_list.reverse()


    if request.method == 'POST':
        if request.POST.has_key('select_tags') or request.POST.has_key('select_conn') or request.POST.has_key(
                'select_ps') or request.POST.has_key('select_thread') or request.POST.has_key('select_net'):
            if request.POST.has_key('select_tags'):
                tagsdefault = request.POST.get('select_tags', None).encode("utf-8")
            elif request.POST.has_key('select_conn'):
                conn_range_default = request.POST.get('select_conn', None)
            elif request.POST.has_key('select_ps'):
                ps_range_default = request.POST.get('select_ps', None)
            elif request.POST.has_key('select_thread'):
                thread_range_default = request.POST.get('select_thread', None)
            elif request.POST.has_key('select_net'):
                net_range_default = request.POST.get('select_net', None)
            return HttpResponseRedirect(
                '/mysql_monitor?tagsdefault=%s&conn_range_default=%s&ps_range_default=%s&thread_range_default=%s&net_range_default=%s' % (
                tagsdefault, conn_range_default, ps_range_default,thread_range_default,net_range_default))

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
    return render_to_response('mysql_mon/mysql_monitor.html', {'messageinfo_list': messageinfo_list, 'msg_num': msg_num,
                                                     'msg_last_content': msg_last_content, 'tim_last': tim_last,
                                                     'conngrow_list': conngrow_list,
                                                     'tagsdefault': tagsdefault, 'conn_range_default': conn_range_default,
                                                     'ps_range_default': ps_range_default,'thread_range_default': thread_range_default, 'net_range_default': net_range_default,
                                                               'tagsinfo': tagsinfo, 'mysqlinfo': mysqlinfo, 'qpsgrow_list': qpsgrow_list, 'threadgrow_list': threadgrow_list, 'netgrow_list': netgrow_list,
                                                               'tpsgrow_list': tpsgrow_list, 'check_status':check_status, 'mysql_status':mysql_status})


@login_required(login_url='/login')
def show_mysql(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()

    # Django自带分页，已不再使用，改为使用前端分页
    dbinfo_list = models_mysql.MysqlDb.objects.all().order_by('mon_status')
    paginator = Paginator(dbinfo_list, 10)
    page = request.GET.get('page')
    try:
        dbinfos = paginator.page(page)
    except PageNotAnInteger:
        dbinfos = paginator.page(1)
    except EmptyPage:
        dbinfos = paginator.page(paginator.num_pages)

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
    return render_to_response('mysql_mon/show_mysql.html',
                              {'dbinfos': dbinfos, 'messageinfo_list': messageinfo_list,
                               'msg_num': msg_num,
                               'msg_last_content': msg_last_content, 'tim_last': tim_last})


@login_required(login_url='/login')
def show_mysql_repl(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    repl_info_list = models_mysql.MysqlRepl.objects.all()
    paginator = Paginator(repl_info_list, 10)
    page = request.GET.get('page')
    try:
        repl_infos = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        repl_infos = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        repl_infos = paginator.page(paginator.num_pages)

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
    return render_to_response('mysql_mon/show_mysql_repl.html',
                              {'repl_infos': repl_infos, 'messageinfo_list': messageinfo_list, 'msg_num': msg_num,
                               'msg_last_content': msg_last_content, 'tim_last': tim_last})

@login_required(login_url='/login')
def show_mysql_rate(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    mysql_rate_list = models_mysql.MysqlDbRate.objects.order_by("db_rate")
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
    return render_to_response('mysql_mon/show_mysql_rate.html',
                              {'mysql_rate_list': mysql_rate_list, 'messageinfo_list': messageinfo_list,
                               'msg_num': msg_num,
                               'msg_last_content': msg_last_content, 'tim_last': tim_last})


@login_required(login_url='/login')
def show_mysql_res(request):

    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    tagsinfo = models_mysql.TabMysqlServers.objects.all()

    tagsdefault = request.GET.get('tagsdefault')

    if not tagsdefault:
        tagsdefault = models_mysql.TabMysqlServers.objects.order_by('tags')[0].tags

     # 时间区间
    range_default = request.GET.get('range_default')
    if not range_default:
        range_default  = '1小时'

    # 主机信息
    begin_time = tools.range(range_default)
    end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    mysql_grow = models_mysql.MysqlDbHis.objects.filter(tags=tagsdefault,uptime__isnull=False).filter(
        chk_time__gt=begin_time, chk_time__lt=end_time).order_by('-chk_time')
    mysql_grow_list = list(mysql_grow)
    mysql_grow_list.reverse()

    dbinfo = models_mysql.MysqlDb.objects.filter(tags=tagsdefault).all()
    big_table_list = models_mysql.MysqlBigTable.objects.filter(tags=tagsdefault).all()

    # alert日志
    mysql_alert_logs = models_oracle.AlertLog.objects.filter(server_type='MySQL',tags=tagsdefault).order_by('-log_time')

    if request.method == 'POST':
        if request.POST.has_key('select_tags') :
            tagsdefault = request.POST.get('select_tags', None).encode("utf-8")
            return HttpResponseRedirect('/show_mysql_res?tagsdefault=%s' %(tagsdefault))
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
    return render_to_response('mysql_mon/show_mysql_res.html', {'tagsdefault': tagsdefault, 'tagsinfo': tagsinfo, 'msg_num':msg_num,
                                                      'msg_last_content': msg_last_content, 'tim_last': tim_last, 'dbinfo':dbinfo,'mysql_grow_list':mysql_grow_list,
                                                      'big_table_list':big_table_list,'mysql_alert_logs':mysql_alert_logs})



@login_required(login_url='/login')
def mysql_big_table(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()

    tags = request.GET.get('tags')
    db = request.GET.get('db')
    table_name = request.GET.get('table_name')

    table_range_default = request.GET.get('table_range_default')

    if not table_range_default:
        table_range_default = '1小时'.decode("utf-8")

    table_begin_time = tools.range(table_range_default)

    end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    tablegrow = models_mysql.MysqlBigTableHis.objects.filter(tags=tags,db=db,table_name=table_name).filter(
        chk_time__gt=table_begin_time, chk_time__lt=end_time).order_by('-chk_time')
    tablegrow_list = list(tablegrow)
    tablegrow_list.reverse()

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
    return render_to_response('mysql_mon/mysql_big_table.html', {'tags': tags, 'table_name':table_name, 'msg_num':msg_num, 'db':db,
                                                      'msg_last_content': msg_last_content, 'tim_last': tim_last,'tablegrow_list':tablegrow_list, })

@login_required(login_url='/login')
def mysql_slowquery(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    tagsinfo = models_mysql.MysqlDb.objects.filter(mon_status='connected')

    tagsdefault = request.GET.get('tagsdefault')
    if not tagsdefault:
        tagsdefault = models_mysql.MysqlDb.objects.filter(mon_status='connected').order_by('tags')[0].tags

    sql = "select host,port,user,password,user_os,password_os from tab_mysql_servers where tags= '%s' " % tagsdefault
    mysql_conf = tools.mysql_query(sql)
    host = mysql_conf[0][0]
    port = mysql_conf[0][1]
    user = mysql_conf[0][2]
    password = mysql_conf[0][3]
    password = base64.decodestring(password)
    user_os = mysql_conf[0][4]
    password_os = mysql_conf[0][5]
    password_os = base64.decodestring(password_os)

    conn = MySQLdb.connect(host=host, user=user, passwd=password, port=int(port), connect_timeout=5, charset='utf8')
    # 获取慢查询日志文件
    slow_log_file = check_msql.get_mysql_para(conn,'slow_query_log_file')
    # 清空历史解析结果
    sql = "delete from mysql_slowquery where tags='%s' " %tagsdefault
    tools.mysql_exec(sql,'')
    # 解析慢查询日志
    logparser.mysql_slow_query(tagsdefault,host,port,user_os,password_os,slow_log_file)


    # 查询解析结果
    sql = """
      select id,
         host,port,start_time,client_host,db_name,substr(sql_text,1,30) sql_text,sql_text sql_text_full,query_time,lock_time,rows_examined,rows_sent
    from mysql_slowquery where tags='%s' order by start_time desc """ %tagsdefault
    slow_query_list = tools.mysql_django_query(sql)


    if request.method == 'POST':
        if request.POST.has_key('select_tags'):
            tagsdefault = request.POST.get('select_tags', None).encode("utf-8")
            return HttpResponseRedirect('/mysql_slowquery?tagsdefault=%s' % (
            tagsdefault))
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
    return render(request, 'mysql_mon/mysql_slowquery.html', {'tagsdefault': tagsdefault, 'tagsinfo':tagsinfo, 'msg_num':msg_num, 'msg_last_content':msg_last_content, 'tim_last':tim_last, 'slow_query_list':slow_query_list})

@login_required(login_url='/login')

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
            return render_to_response('mysql_mon/mysql_ctl.html',
                                      {'messageinfo_list': messageinfo_list, 'mysql_ctls': mysql_ctls,
                                       'msg_num': msg_num, 'now': now,
                                       'msg_last_content': msg_last_content, 'tim_last': tim_last})
        else:
            msg_num = 0
            msg_last_content = ''
            tim_last = ''
            return render_to_response('mysql_mon/mysql_ctl.html',
                                      {'messageinfo_list': messageinfo_list, 'mysql_ctls': mysql_ctls, 'now': now,
                                       'msg_last_content': msg_last_content, 'tim_last': tim_last})

@login_required(login_url='/login')
def get_mysql_errorlog(request):

    tags = request.GET.get('tags')

    sql = '''select host,port,user,password,user_os,password_os,ssh_port_os,logfile from tab_mysql_servers where tags='%s' ''' % tags
    mysqlinfo = tools.mysql_query(sql)
    host,port,user,password,user_os,password_os,ssh_port_os,logfile = mysqlinfo[0]
    password = base64.decodestring(password)
    password_os = base64.decodestring(password_os)
    if not logfile:
        # 后台日志参数
        conn = MySQLdb.connect(host=host, user=user, passwd=password, port=int(port), connect_timeout=5, charset='utf8')
        logfile = tools.get_mysql_para(conn, 'log_error')

    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(host, ssh_port_os, user_os, password_os)
    command = 'tail -300 %s' %logfile
    std_in, std_out, std_err = ssh_client.exec_command(command)
    errorlog = std_out.read()

    return render_to_response('frame/show_log.html',
                              {'tags':tags,'log':errorlog})
