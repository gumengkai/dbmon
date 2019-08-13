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
import oracle_mon.models as models_oracle
import frame.oracle_do as ora_do
import frame.tools as tools
import frame.oracle_backupinfo as oracle_backupinfo
import tasks as task
from django.contrib import messages
import os
import commands
import paramiko
import cx_Oracle
# Create your views here.


@login_required(login_url='/login')
def oracle_monitor(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    tagsinfo = models_oracle.TabOracleServers.objects.all().order_by('tags')

    tagsdefault = request.GET.get('tagsdefault')
    if not tagsdefault:
        tagsdefault = models_oracle.TabOracleServers.objects.order_by('tags')[0].tags

    conn_range_default = request.GET.get('conn_range_default')
    if not conn_range_default:
        conn_range_default = '1小时'.decode("utf-8")

    undo_range_default = request.GET.get('undo_range_default')
    if not undo_range_default:
        undo_range_default = '1小时'.decode("utf-8")

    tmp_range_default = request.GET.get('tmp_range_default')
    if not tmp_range_default:
        tmp_range_default = '1小时'.decode("utf-8")

    ps_range_default = request.GET.get('ps_range_default')
    if not ps_range_default:
        ps_range_default = '1小时'.decode("utf-8")

    conn_begin_time = tools.range(conn_range_default)
    undo_begin_time = tools.range(undo_range_default)
    tmp_begin_time = tools.range(tmp_range_default)
    ps_begin_time = tools.range(ps_range_default)

    end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # 取当前数据库状态
    try:
        oracle_curr = models_oracle.OracleDb.objects.filter(tags=tagsdefault).get(
            tags=tagsdefault, )
    except models_oracle.OracleDb.DoesNotExist:
        oracle_curr = \
            models_oracle.OracleDbHis.objects.filter(tags=tagsdefault).order_by(
                '-chk_time')[0]
    # 取上一次有效采集的数据
    try:
        try:
            oracleinfo = models_oracle.OracleDb.objects.filter(tags=tagsdefault, percent_process__isnull=False).get(tags=tagsdefault,)
        except models_oracle.OracleDb.DoesNotExist:
            oracleinfo = \
            models_oracle.OracleDbHis.objects.filter(tags=tagsdefault, percent_process__isnull=False).order_by(
                '-chk_time')[0]
    except Exception, e:
        oracleinfo = \
            models_oracle.OracleDbHis.objects.filter(tags=tagsdefault).order_by(
                '-chk_time')[0]

    if oracle_curr.mon_status == 'connected':
        check_status = 'success'
        oracle_status = '在线'
    else:
        check_status = 'danger'
        oracle_status = '离线'


    eventinfo = models_oracle.OracleDbEvent.objects.filter(tags=tagsdefault)
    lockinfo = models_oracle.OracleLock.objects.filter(tags=tagsdefault)

    conngrow = models_oracle.OracleDbHis.objects.filter(tags=tagsdefault, percent_process__isnull=False).filter(
        chk_time__gt=conn_begin_time, chk_time__lt=end_time).order_by('-chk_time')
    conngrow_list = list(conngrow)
    conngrow_list.reverse()

    try:
        undoinfo = models_oracle.OracleUndoTbs.objects.get(tags=tagsdefault)
    except models_oracle.OracleUndoTbs.DoesNotExist:
        undoinfo =  models_oracle.OracleUndoTbsHis.objects.filter(tags=tagsdefault, pct_used__isnull=False).order_by('-chk_time')
        if not undoinfo:
            models_oracle.OracleUndoTbsHis.objects.create(tags=tagsdefault,undo_tbs_name='UNDOTBS1', total_mb=0, used_mb=0,
                                                        pct_used=0,rate_level='green')
        undoinfo = models_oracle.OracleUndoTbsHis.objects.filter(tags=tagsdefault, pct_used__isnull=False).order_by('-chk_time')[0]


    undogrow = models_oracle.OracleUndoTbsHis.objects.filter(tags=tagsdefault, pct_used__isnull=False).filter(
        chk_time__gt=undo_begin_time, chk_time__lt=end_time).order_by('-chk_time')
    undogrow_list = list(undogrow)
    undogrow_list.reverse()

    try:
        tmpinfo = models_oracle.OracleTmpTbs.objects.get(tags=tagsdefault,tmp_tbs_name='TEMP')
    except models_oracle.OracleTmpTbs.DoesNotExist:
        tmpinfo =  models_oracle.OracleTmpTbsHis.objects.filter(tags=tagsdefault, pct_used__isnull=False).order_by('-chk_time')
        if not tmpinfo:
            models_oracle.OracleTmpTbsHis.objects.create(tags=tagsdefault, tmp_tbs_name='UNDOTBS1', total_mb=0,
                                                          used_mb=0,
                                                          pct_used=0, rate_level='green')
        tmpinfo = models_oracle.OracleTmpTbsHis.objects.filter(tags=tagsdefault, pct_used__isnull=False).order_by('-chk_time')[0]

    tmpgrow = models_oracle.OracleTmpTbsHis.objects.filter(tags=tagsdefault, pct_used__isnull=False).filter(
        chk_time__gt=tmp_begin_time, chk_time__lt=end_time).order_by('-chk_time')
    tmpgrow_list = list(tmpgrow)
    tmpgrow_list.reverse()

    psgrow = models_oracle.OracleDbHis.objects.filter(tags=tagsdefault, qps__isnull=False).filter(
        chk_time__gt=ps_begin_time, chk_time__lt=end_time).order_by('-chk_time')
    psgrow_list = list(psgrow)
    psgrow_list.reverse()
    # 连接信息
    sql = "select host,port,service_name,user,password,user_os,password_os from tab_oracle_servers where tags= '%s' " % tagsdefault
    oracle = tools.mysql_query(sql)
    host = oracle[0][0]
    port = oracle[0][1]
    service_name = oracle[0][2]
    user = oracle[0][3]
    password = oracle[0][4]
    password = base64.decodestring(password)
    url = host + ':' + port + '/' + service_name

    if request.method == 'POST':
        if request.POST.has_key('select_tags') or request.POST.has_key('select_conn') or request.POST.has_key('select_undo') or request.POST.has_key('select_tmp') or request.POST.has_key('select_ps'):
            if request.POST.has_key('select_tags'):
                tagsdefault = request.POST.get('select_tags', None).encode("utf-8")
            elif request.POST.has_key('select_conn'):
                conn_range_default = request.POST.get('select_conn',None)
            elif request.POST.has_key('select_undo'):
                undo_range_default = request.POST.get('select_undo', None)
            elif request.POST.has_key('select_tmp'):
                tmp_range_default = request.POST.get('select_tmp', None)
            elif request.POST.has_key('select_ps'):
                ps_range_default = request.POST.get('select_ps', None)
            return HttpResponseRedirect('/oracle_monitor?tagsdefault=%s&conn_range_default=%s&undo_range_default=%s&tmp_range_default=%s&ps_range_default=%s' %(tagsdefault,conn_range_default,undo_range_default,tmp_range_default,ps_range_default))

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
    return render_to_response('oracle_mon/oracle_monitor.html',
                              {'conngrow_list': conngrow_list, 'undogrow_list': undogrow_list, 'tmpinfo': tmpinfo,
                               'tmpgrow_list': tmpgrow_list,'psgrow_list': psgrow_list, 'tagsdefault': tagsdefault, 'tagsinfo': tagsinfo,
                               'oracleinfo': oracleinfo, 'undoinfo': undoinfo, 'eventinfo': eventinfo,
                               'lockinfo': lockinfo, 'messageinfo_list': messageinfo_list,
                               'msg_num': msg_num, 'conn_range_default': conn_range_default,
                               'undo_range_default': undo_range_default, 'tmp_range_default': tmp_range_default,'ps_range_default': ps_range_default,
                               'msg_last_content': msg_last_content, 'tim_last': tim_last,'check_status':check_status,'oracle_status':oracle_status})

@login_required(login_url='/login')
def show_oracle(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    dbinfo_list = models_oracle.OracleDb.objects.order_by("rate_level")
    paginator = Paginator(dbinfo_list, 10)
    page = request.GET.get('page')
    try:
        dbinfos = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        dbinfos = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
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
    return render_to_response('oracle_mon/show_oracle.html',
                              {'dbinfos': dbinfos, 'messageinfo_list': messageinfo_list, 'msg_num': msg_num,
                               'msg_last_content': msg_last_content, 'tim_last': tim_last})


@login_required(login_url='/login')
def show_oracle_resource(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    tagsinfo = models_oracle.OracleDb.objects.filter(mon_status='connected')

    tagsdefault = request.GET.get('tagsdefault')
    if not tagsdefault:
        tagsdefault = models_oracle.OracleDb.objects.filter(mon_status='connected').order_by('tags')[0].tags
    typedefault = request.GET.get('typedefault')

    redo_range_default = request.GET.get('redo_range_default')
    if not redo_range_default:
        redo_range_default  = 7

    tbsinfo_list = models_oracle.OracleTbs.objects.filter(tags=tagsdefault).order_by('-pct_used')
    # 分页
    paginator_tbs = Paginator(tbsinfo_list, 5)
    undotbsinfo_list = models_oracle.OracleUndoTbs.objects.filter(tags=tagsdefault).order_by('-pct_used')
    paginator_undo = Paginator(undotbsinfo_list, 5)
    tmptbsinfo_list = models_oracle.OracleTmpTbs.objects.filter(tags=tagsdefault).order_by('-pct_used')
    paginator_tmp = Paginator(tmptbsinfo_list, 5)

    page_tbs = request.GET.get('page_tbs')
    try:
        tbsinfos = paginator_tbs.page(page_tbs)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        tbsinfos = paginator_tbs.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        tbsinfos = paginator_tbs.page(paginator_tbs.num_pages)
    page_undo = request.GET.get('page_undo')
    try:
        undotbsinfos = paginator_undo.page(page_undo)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        undotbsinfos = paginator_undo.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        undotbsinfos = paginator_undo.page(paginator_undo.num_pages)
    page_tmp = request.GET.get('page_tmp')
    try:
        tmptbsinfos = paginator_undo.page(page_tmp)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        tmptbsinfos = paginator_tmp.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        tmptbsinfos = paginator_tmp.page(paginator_tmp.num_pages)

    # 获取控制文件信息
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
        select name,round(block_size*file_size_blks/1024/1024,2) size_M,'controlfile' tpye  from v$controlfile
          """
    oracle_controlfiles = tools.oracle_django_query(user, password, url, sql)
    # 获取在线日志
    sql = """
    select a.GROUP# group_no,b.THREAD# thread_no,a.TYPE,b.SEQUENCE# sequence_no,b.BYTES/1024/1024 SIZE_M,b.ARCHIVED,b.STATUS,a.MEMBER from v$logfile a,v$log b where a.GROUP#=b.GROUP#(+)
    """
    oracle_redo_files = tools.oracle_django_query(user, password, url, sql)
    # 在线日志统计
    if redo_range_default == '1':
        sql = """
        select  'hh'||to_char(first_time, 'hh24') stat_date,
            count(1) log_count,
            (select bytes / 1024 / 1024 sizem from v$log where rownum < 2) log_size
       from v$log_history
      where to_char(first_time, 'yyyymmdd') < to_char(sysdate, 'yyyymmdd')
        and to_char(first_time, 'yyyymmdd') >=
            to_char(sysdate - 1, 'yyyymmdd')
      group by to_char(first_time, 'hh24'),to_char(first_time, 'dy')
      order by to_char(first_time, 'hh24')
        """
        oracle_redo_cnts = tools.oracle_django_query(user, password, url, sql)
    else:
        sql = """ select to_char(first_time, 'yyyy-mm-dd') stat_date,
               count(1) log_count,
               (select bytes / 1024 / 1024 sizem from v$log where rownum < 2) log_size
          from v$log_history
         where to_char(first_time, 'yyyymmdd') < to_char(sysdate, 'yyyymmdd')
         and to_char(first_time, 'yyyymmdd') >= to_char(sysdate-%s, 'yyyymmdd')
         group by to_char(first_time, 'yyyy-mm-dd'), to_char(first_time, 'dy')  order by to_char(first_time, 'yyyy-mm-dd')""" % redo_range_default
        oracle_redo_cnts = tools.oracle_django_query(user, password, url, sql)
    # 表变化记录
    sql = """
        select table_owner,table_name,inss,upds,dels,
               to_char(inss + upds + dels) dmls,to_char(sysdate , 'yyyy-mm-dd') get_date,truncated,num_rows,
               to_char(last_analyzed  ,'yyyy-mm-dd hh24:mi:ss') last_analyzed
        from (select m.table_owner, m.table_name, inserts as inss, updates as upds, deletes as dels, truncated, t.num_rows,t.last_analyzed
            from sys.dba_tab_modifications m, dba_tables t
            where m.table_name = t.table_name
            and t.owner not in ('SYS','SYSTEM','OUTLN','DIP','ORACLE_OCM','DBSNMP','APPQOSSYS','WMSYS','EXFSYS',
            'CTXSYS','ANONYMOUS','XDB','XS$NULL','ORDDATA','SI_INFORMTN_SCHEMA','ORDPLUGINS','ORDSYS','MDSYS','OLAPSYS',
            'MDDATA','SPATIAL_WFS_ADMIN_USR','SPATIAL_CSW_ADMIN_USR','SYSMAN','MGMT_VIEW','APEX_030200','FLOWS_FILES',
            'APEX_PUBLIC_USER','OWBSYS','OWBSYS_AUDIT','SCOTT')
            and m.table_owner = t.owner and m.partition_name is null)
        """
    oracle_table_changes = tools.oracle_django_query(user, password, url, sql)
    # 序列
    sql = """
        select sequence_owner,sequence_name,min_value,max_value,increment_by,cycle_flag,order_flag,
               cache_size,last_number,
               round((max_value - last_number) / (max_value - min_value), 2) * 100 pct_used,
               (case when (round((max_value - last_number) / (max_value - min_value), 2) * 100) > 30 
                       then 'green'
                      when (round((max_value - last_number) / (max_value - min_value), 2) * 100) <= 30 and (round((max_value - last_number) / (max_value - min_value), 2) * 100) > 10
                       then 'yellow'
                      when (round((max_value - last_number) / (max_value - min_value), 2) * 100) <= 10
                      then 'red'
                      else ''
                     end) seq_color,
               to_char(sysdate, 'yyyy-mm-dd') last_analyzed
          from dba_sequences s
         where s.sequence_owner not in ('SYS','SYSTEM','OUTLN','DIP','ORACLE_OCM','DBSNMP','APPQOSSYS','WMSYS','EXFSYS',
        'CTXSYS','ANONYMOUS','XDB','XS$NULL','ORDDATA','SI_INFORMTN_SCHEMA','ORDPLUGINS','ORDSYS','MDSYS','OLAPSYS',
        'MDDATA','SPATIAL_WFS_ADMIN_USR','SPATIAL_CSW_ADMIN_USR','SYSMAN','MGMT_VIEW','APEX_030200','FLOWS_FILES',
        'APEX_PUBLIC_USER','OWBSYS','OWBSYS_AUDIT','SCOTT')
        """
    oracle_sequences = tools.oracle_django_query(user, password, url, sql)
    # 账号
    sql = """
        select username,profile,to_char(created,'yyyy-mm-dd hh24:mi:ss') created,
               account_status,
              (case when account_status <> 'OPEN' then 'red' else 'green'end ) account_color,
               to_char(lock_date,'yyyy-mm-dd hh24:mi:ss') lock_date,
               to_char(expiry_date,'yyyy-mm-dd hh24:mi:ss') expiry_date,
               (case when expiry_date - sysdate > 30 
                       then 'green'
                      when expiry_date - sysdate <= 30 and expiry_date - sysdate > 7 
                       then 'yellow'
                      when expiry_date - sysdate <= 7 
                      then 'red'
                      else ''
                     end) expiry_color,default_tablespace,temporary_tablespace
        from dba_users order by created desc
        """
    oracle_users = tools.oracle_django_query(user, password, url, sql)

    # alert日志
    oracle_alert_logs = models_oracle.AlertLog.objects.filter(server_type='Oracle',tags=tagsdefault).order_by('-log_time')


    if request.method == 'POST':
        if request.POST.has_key('select_tags') :
            tagsdefault = request.POST.get('select_tags', None).encode("utf-8")
            return HttpResponseRedirect('/show_oracle_resource?tagsdefault=%s&redo_range_default=%s' %(tagsdefault,redo_range_default))
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
    return render_to_response('oracle_mon/show_oracle_res.html', {'tagsdefault': tagsdefault, 'typedefault':typedefault, 'tagsinfo': tagsinfo, 'msg_num':msg_num,
                                                      'msg_last_content': msg_last_content, 'tim_last': tim_last,
                                                       'tbsinfos': tbsinfos, 'undotbsinfos': undotbsinfos,'tmptbsinfos': tmptbsinfos,'oracle_controlfiles':oracle_controlfiles,
                                                       'oracle_redo_files':oracle_redo_files,'oracle_redo_cnts':oracle_redo_cnts, 'oracle_table_changes':oracle_table_changes,
                                                                  'oracle_sequences':oracle_sequences, 'oracle_users':oracle_users, 'oracle_alert_logs':oracle_alert_logs})


@login_required(login_url='/login')
def oracle_profile(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    tags = request.GET.get('tags')
    profile_name = request.GET.get('profile_name')
    sql = "select host,port,service_name,user,password,user_os,password_os from tab_oracle_servers where tags= '%s' " %tags
    oracle = tools.mysql_query(sql)
    host = oracle[0][0]
    port = oracle[0][1]
    service_name = oracle[0][2]
    user = oracle[0][3]
    password = oracle[0][4]
    password = base64.decodestring(password)
    url = host + ':' + port + '/' + service_name
    sql = """
        select profile,resource_name,resource_type,limit,to_char(sysdate,'yyyy-mm-dd') get_date
          from dba_profiles where  profile = '%s'
        """ %profile_name

    oracle_profiles = tools.oracle_django_query(user,password,url,sql)

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
    return render_to_response('oracle_mon/oracle_profile.html',
                              {'messageinfo_list': messageinfo_list,'msg_num':msg_num, 'oracle_profiles': oracle_profiles, 'profile_name':profile_name,'tags': tags,
                               'now': now,
                               'msg_last_content': msg_last_content, 'tim_last': tim_last})

@login_required(login_url='/login')
def oracle_grant(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    tags = request.GET.get('tags')
    username = request.GET.get('username')
    sql = "select host,port,service_name,user,password,user_os,password_os from tab_oracle_servers where tags= '%s' " %tags
    oracle = tools.mysql_query(sql)
    host = oracle[0][0]
    port = oracle[0][1]
    service_name = oracle[0][2]
    user = oracle[0][3]
    password = oracle[0][4]
    password = base64.decodestring(password)
    url = host + ':' + port + '/' + service_name
    # 角色权限
    sql = """
         select grantee,
         granted_role,
         admin_option,
         default_role,
         to_char(sysdate, 'yyyy-mm-dd') get_date
         from dba_role_privs where grantee = '%s'
        """ %username
    user_roles = tools.oracle_django_query(user,password,url,sql)
    # 系统权限
    sql = """
        select grantee,privilege,admin_option,to_char(sysdate,'yyyy-mm-dd') get_date
          from dba_sys_privs where grantee = '%s'
        """ %username
    sys_privs = tools.oracle_django_query(user,password,url,sql)
    # 对象权限
    sql = """
        select owner,grantee,grantor,table_name,privilege
               ,grantable,hierarchy,to_char(sysdate,'yyyy-mm-dd') get_date
          from dba_tab_privs
         where grantee <> 'PUBLIC' and privilege <> 'EXECUTE' and grantee = '%s'
        """ %username
    tab_privs = tools.oracle_django_query(user,password,url,sql)

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
    return render_to_response('oracle_mon/oracle_grant.html',
                              {'messageinfo_list': messageinfo_list, 'msg_num':msg_num,'user_roles': user_roles,'sys_privs':sys_privs,
                               'tab_privs':tab_privs,'username':username,'tags': tags,'now': now,
                               'msg_last_content': msg_last_content, 'tim_last': tim_last})

@login_required(login_url='/login')
def show_oracle_rate(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    oracle_rate_list = models_oracle.OracleDbRate.objects.order_by("db_rate")
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
    return render_to_response('oracle_mon/show_oracle_rate.html',
                              {'oracle_rate_list': oracle_rate_list, 'messageinfo_list': messageinfo_list,
                               'msg_num': msg_num,
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
       b.sid,
       a.spid,
       ROUND(a.PGA_USED_MEM/1024/1024,2) PGA_USED_MEM,
       ROUND(a.PGA_ALLOC_MEM/1024/1024,2) PGA_ALLOC_MEM,
       ROUND(a.PGA_FREEABLE_MEM/1024/1024,2) PGA_FREEABLE_MEM,
       ROUND(a.PGA_MAX_MEM/1024/1024,2) PGA_MAX_MEM
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
    return render_to_response('oracle_mon/oracle_pga.html',
                              {'messageinfo_list': messageinfo_list,'oracle_pgas':oracle_pgas,
                               'tags': tags,
                               'msg_num': msg_num, 'now': now,
                               'msg_last_content': msg_last_content, 'tim_last': tim_last})


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
        return render_to_response('oracle_mon/oracle_lock_manage.html',
                                  {'messageinfo_list': messageinfo_list, 'oracle_locks': oracle_locks,
                                   'msg_num': msg_num, 'now': now,
                                   'msg_last_content': msg_last_content, 'tim_last': tim_last})
    else:
        msg_num = 0
        msg_last_content = ''
        tim_last = ''
        return render_to_response('oracle_mon/oracle_lock_manage.html',
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
        return render_to_response('oracle_mon/oracle_session.html',
                                  {'messageinfo_list': messageinfo_list, 'oracle_sessions': oracle_sessions,'tags':tags,
                                   'msg_num': msg_num, 'now': now,
                                   'msg_last_content': msg_last_content, 'tim_last': tim_last})
    else:
        msg_num = 0
        msg_last_content = ''
        tim_last = ''
        return render_to_response('oracle_mon/oracle_session.html',
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
    return render_to_response('oracle_mon/oracle_process.html',
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
             where tablespace_name like 'UNDO%'
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
    return render_to_response('oracle_mon/oracle_undo.html',
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
    return render_to_response('oracle_mon/oracle_temp.html',
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
    return render_to_response('oracle_mon/oracle_active_session.html',
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
    return render_to_response('oracle_mon/oracle_waiting_session.html',
                              {'messageinfo_list': messageinfo_list,'oracle_waiting_sessions':oracle_waiting_sessions,
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
    return render_to_response('oracle_mon/oracle_para.html',
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
        p_sql = "select host,port,service_name,user,password,user_os,password_os,ssh_port_os from tab_oracle_servers where tags= '%s' " % p_tags
        p_ssh = tools.mysql_query(p_sql)
        p_host = p_ssh[0][0]
        p_user = p_ssh[0][5]
        p_password = p_ssh[0][6]
        p_password = base64.decodestring(p_password)
        p_ssh_port = p_ssh[0][7]
        s_sql = "select host,port,service_name,user,password,user_os,password_os,ssh_port_os from tab_oracle_servers where tags= '%s' " % s_tags
        s_ssh = tools.mysql_query(s_sql)
        s_host = s_ssh[0][0]
        s_user = s_ssh[0][5]
        s_password = s_ssh[0][6]
        s_password = base64.decodestring(s_password)
        s_ssh_port = s_ssh[0][7]
        task.oracle_switchover.delay(p_tags,p_host,p_user,p_password,p_ssh_port,s_tags,s_host,s_user,s_password,s_ssh_port)
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
    sql_refresh = 'update oracle_switchover t1 set t1.standby_curr_role = (select database_role from oracle_db where tags=t1.standby_tags),t1.adg_trans_lag =(select adg_transport_lag from oracle_db where tags=t1.standby_tags),t1.adg_apply_lag=(select adg_apply_lag from oracle_db where tags=t1.standby_tags)'
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
    return render(request, 'oracle_mon/oracle_switchover.html',
                  {'messageinfo_list': messageinfo_list, 'oracle_switchovers': oracle_switchovers, 'log_type': log_type, 'now': now,'msg_num':msg_num,
                               'msg_last_content': msg_last_content, 'tim_last': tim_last})

@login_required(login_url='/login')
def oracle_top_sql(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    tagsinfo = models_oracle.OracleDb.objects.all().filter(mon_status='connected',open_mode='READ WRITE').order_by('tags')

    tagsdefault = request.GET.get('tagsdefault')
    if not tagsdefault:
        tagsdefault = models_oracle.OracleDb.objects.filter(mon_status='connected',open_mode='READ WRITE').order_by('tags')[0].tags
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
    return render_to_response('oracle_mon/oracle_top_sql.html', {'tagsdefault': tagsdefault, 'tagsinfo': tagsinfo, 'msg_num':msg_num,
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
    return render_to_response('oracle_mon/oracle_sql.html',
                              {'messageinfo_list': messageinfo_list,'sql_id':sql_id, 'sql_texts': sql_texts,'sql_plans':sql_plans, 'tags': tags,
                               'now': now,'msg_num':msg_num,
                               'msg_last_content': msg_last_content, 'tim_last': tim_last})


@login_required(login_url='/login')
def oracle_backup(request):
    tagsinfo = models_oracle.TabOracleServers.objects.all().order_by('tags')

    tagsdefault = request.GET.get('tagsdefault')
    if not tagsdefault:
        tagsdefault = models_oracle.TabOracleServers.objects.order_by('tags')[0].tags

    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    now = tools.now()

    # 收集oracle备份数据
    oracle_backupinfo.do_collect()

    oracle_backups = models_oracle.OracleBackupInfo.objects.filter(tags=tagsdefault)

    oracle_backup_pieces = models_oracle.OracleBackupPiece.objects.filter(tags=tagsdefault)


    # 加载Oracle备份任务
    oracle_bak_job = '''select t1.job_no,t1.job_name,t1.tags,t1.bak_conf_no,t1.bak_conf_name,t2.bak_type,
     (case t1.is_on when 1 then 'on' else 'off' end) is_on,
     (case t1.is_on when 1 then 'green' else 'red' end) is_on1,t1.next_bak_time from oracle_bak_job t1 left join bak_conf t2 on t1.bak_conf_no=t2.conf_no '''
    oracle_bak_jobs = tools.mysql_django_query( oracle_bak_job)

    if request.method == 'POST':
        if request.POST.has_key('select_tags') :
            tagsdefault = request.POST.get('select_tags', None).encode("utf-8")
            return HttpResponseRedirect('/oracle_backup?tagsdefault=%s' %(tagsdefault))
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
    return render_to_response('oracle_mon/oracle_backup.html', {'messageinfo_list': messageinfo_list, 'msg_num':msg_num, 'msg_last_content':msg_last_content, 'tim_last':tim_last,
                                                   'now': now,'oracle_backups':oracle_backups,'oracle_backup_pieces':oracle_backup_pieces,'oracle_bak_jobs':oracle_bak_jobs,
                                                     'tagsinfo':tagsinfo,'tagsdefault':tagsdefault})

@login_required(login_url='/login')
def oracle_rpt(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    tagsinfo = models_oracle.OracleDb.objects.filter(mon_status='connected')

    tagsdefault = request.GET.get('tagsdefault')
    if not tagsdefault:
        tagsdefault = models_oracle.OracleDb.objects.filter(mon_status='connected').order_by('tags')[0].tags
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
    user_os = oracle[0][5]
    password_os = oracle[0][6]
    password_os = base64.decodestring(password_os)
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

    start_time = (datetime.datetime.now() + datetime.timedelta(hours=-1)).strftime("%Y-%m-%d %H:%M:%S")
    end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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
            task.get_report.delay(tagsdefault,user,password,url,report_type,begin_snap,end_snap)
            messages.add_message(request, messages.SUCCESS, '正在生成')

        elif request.POST.has_key('commit_event'):
            start_time = request.POST.get('startTime', None)
            end_time = request.POST.get('endTime', None)

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
               to_date('%s','YYYY-MM-DD HH24:MI:SS') AND
               to_date('%s','YYYY-MM-DD HH24:MI:SS')
         GROUP BY a.program, a.sql_id, a.session_state, a.event
         ORDER BY percent DESC)
     WHERE ROWNUM <= 30 ''' %(start_time,end_time)

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
    return render(request, 'oracle_mon/oracle_rpt.html', {'tagsdefault': tagsdefault, 'typedefault':typedefault, 'tagsinfo': tagsinfo, 'msg_num':msg_num,
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
    user_os = oracle[0][5]
    password_os = oracle[0][6]
    password_os = base64.decodestring(password_os)
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

    start_time = (datetime.datetime.now() + datetime.timedelta(hours=-1)).strftime("%Y-%m-%d %H:%M:%S")
    end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


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
            begin_snap = request.POST.get('ashstartTime', None)
            end_snap = request.POST.get('ashendTime', None)
            task.get_report.delay(tagsdefault,user,password,url,report_type,begin_snap,end_snap)
            messages.add_message(request, messages.SUCCESS, '正在生成')

        elif request.POST.has_key('commit_event'):
            start_time = request.POST.get('startTime', None)
            end_time = request.POST.get('endTime', None)
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
               to_date('%s','YYYY-MM-DD HH24:MI:SS') AND
               to_date('%s','YYYY-MM-DD HH24:MI:SS')
         GROUP BY a.program, a.sql_id, a.session_state, a.event
         ORDER BY percent DESC)
     WHERE ROWNUM <= 30 ''' %(start_time,end_time)

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

    return render(request, 'oracle_mon/oracle_rpt_ash.html', {'tagsdefault': tagsdefault, 'typedefault':typedefault, 'tagsinfo': tagsinfo, 'msg_num':msg_num,
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
        return render_to_response('frame/show_txt.html', {'aList':list})
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
    return render_to_response('oracle_mon/oracle_tbs.html', {'tags': tags, 'tbs_name':tbs_name, 'msg_num':msg_num,
                                                      'msg_last_content': msg_last_content, 'tim_last': tim_last,'tbsgrow_list':tbsgrow_list,
                                                  'oracle_tbs_segments':oracle_tbs_segments,'oracle_pers':oracle_pers,'max_tbs_used':max_tbs_used})


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
    return render(request, 'oracle_mon/oracle_perf.html', {'tagsdefault': tagsdefault, 'tagsinfo': tagsinfo, 'msg_num':msg_num,
                                                'msg_last_content': msg_last_content, 'tim_last': tim_last,
                                               'dbgrow_list':dbgrow_list})

@login_required(login_url='/login')
def oracle_logminer(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    tagsinfo = models_oracle.TabOracleServers.objects.all()

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

    log_list = models_oracle.OracleLogmnr.objects.values()

    if request.method == 'POST':
        if request.POST.has_key('select_tags'):
            tagsdefault = request.POST.get('select_tags', None).encode("utf-8")
            return HttpResponseRedirect('/oracle_logminer?tagsdefault=%s' % (
            tagsdefault))
        elif request.POST.has_key('commit'):
            schema = request.POST.get('schema', None)
            object = request.POST.get('object', None)
            operation = request.POST.get('operation', None)
            task.oracle_logmnr.delay(tagsdefault,url,user,password,schema,object,operation,log_list)
            messages.add_message(request, messages.SUCCESS, '正在解析')

        else:
            logout(request)
            return HttpResponseRedirect('/login/')

    # 查询解析结果
    sql = """
      select
         id id, 
         timestamp,
         operation,
         rollback,
         seg_owner,
         seg_name,
         table_name,
         seg_type_name,
         table_space,
         username,
         os_username,
         machine_name,
         session#,
         substr(sql_undo,1,20) sql_undo,
         sql_undo sql_undo_text,
         substr(sql_redo,1,20) sql_redo,
         sql_redo sql_redo_text
    from logmnr_contents order by timestamp desc """
    logmnr_contents = tools.oracle_django_query(user, password, url, sql)

    if messageinfo_list:
        msg_num = len(messageinfo_list)
        msg_last = models_frame.TabAlarmInfo.objects.latest('id')
        msg_last_content = msg_last.alarm_content
        tim_last = (datetime.datetime.now() - msg_last.alarm_time).seconds / 60
    else:
        msg_num = 0
        msg_last_content = ''
        tim_last = ''
    return render(request, 'oracle_mon/oracle_logminer.html', {'tagsdefault': tagsdefault, 'tagsinfo':tagsinfo, 'msg_num':msg_num, 'msg_last_content':msg_last_content, 'tim_last':tim_last, 'log_list':log_list, 'logmnr_contents':logmnr_contents})



@login_required(login_url='/login')
def oracle_logs_add(request):
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
    # 查询在线日志
    sql = """
        select a.GROUP# group_no,b.THREAD# thread_no,a.TYPE,b.SEQUENCE# sequence_no,first_time,next_time,b.BYTES/1024/1024 SIZE_M,b.ARCHIVED,b.STATUS,a.MEMBER from v$logfile a,v$log b where a.GROUP#=b.GROUP#(+)
        """
    oracle_redo_files = tools.oracle_django_query(user,password,url,sql)
    # 查询归档日志
    sql = """
     select sequence# sequence_no,first_time, next_time, round(blocks*block_size/1024/1024,2) mb,name from v$archived_log where archived='YES' and deleted='NO' and STANDBY_DEST='NO'
    """
    oracle_archived_files = tools.oracle_django_query(user,password,url,sql)
    status = 0

    if request.method == "POST":
        # 添加日志或归档日志
        if request.POST.has_key('commit'):
            check_box_list = request.POST.getlist('check_box_list')
            status = 1
            sql = "delete from oracle_logmnr"
            tools.mysql_exec(sql,'')
            for log in check_box_list:
                sql = "insert into oracle_logmnr(logfile) values('%s')" %log
                tools.mysql_exec(sql,'')
        elif request.POST.has_key('logout'):
            logout(request)
            return HttpResponseRedirect('/login/')


    return render_to_response('oracle_mon/oracle_logs_add.html', {'oracle_redo_files':oracle_redo_files, 'oracle_archived_files':oracle_archived_files, 'status':status})

@login_required(login_url='/login')
def show_sqltext(request):
    tags = request.GET.get('tags')
    id = request.GET.get('id')

    sql = "select host,port,service_name,user,password,user_os,password_os from tab_oracle_servers where tags= '%s' " % tags
    oracle = tools.mysql_query(sql)
    host = oracle[0][0]
    port = oracle[0][1]
    service_name = oracle[0][2]
    user = oracle[0][3]
    password = oracle[0][4]
    password = base64.decodestring(password)
    url = host + ':' + port + '/' + service_name

    sql = "select sql_undo,sql_redo from logmnr_contents where id =%s " %int(id)

    sqltext = tools.oracle_django_query(user, password, url, sql)

    return render_to_response('oracle_mon/show_sqltext.html', {'sqltext':sqltext})

@login_required(login_url='/login')
def oracle_audit(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    tagsinfo = models_oracle.TabOracleServers.objects.all()

    tagsdefault = request.GET.get('tagsdefault')
    owner = request.GET.get('owner','')
    object = request.GET.get('object','')

    db_range_default = request.GET.get('db_range_default')

    if not db_range_default:
        db_range_default = '1小时'.decode("utf-8")

    begin_time = tools.range(db_range_default)
    end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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

    if request.method == 'POST':
        if request.POST.has_key('select_tags'):
            tagsdefault = request.POST.get('select_tags', None).encode("utf-8")
            return HttpResponseRedirect('/oracle_audit?tagsdefault=%s&db_range_default=%s&owner=%s&object=%s' % (tagsdefault,db_range_default,owner,object))

        elif request.POST.has_key('commit'):
            owner = request.POST.get('owner','')
            object = request.POST.get('object','')
            return HttpResponseRedirect('/oracle_audit?tagsdefault=%s&db_range_default=%s&owner=%s&object=%s' % (tagsdefault,db_range_default,owner,object))
        else:
            logout(request)
            return HttpResponseRedirect('/login/')

    # 查询解析结果
    sql = """
      select os_username,
       username,
       userhost,
       terminal,
       timestamp,
       owner,
       obj_name,
       action_name,
       priv_used,
       sql_bind,
       sql_text
  from dba_audit_trail where  action_name not in ('LOGON','LOGOFF') 
  and owner like nvl(upper('%s'),owner) and obj_name like nvl(upper('%s'),obj_name) 
  and timestamp > to_date('%s','yyyy-mm-dd hh24:mi:ss') and timestamp < to_date('%s','yyyy-mm-dd hh24:mi:ss')  
  order by scn desc""" %(owner,object,begin_time,end_time)

    audit_contents = tools.oracle_django_query(user, password, url, sql)

    if messageinfo_list:
        msg_num = len(messageinfo_list)
        msg_last = models_frame.TabAlarmInfo.objects.latest('id')
        msg_last_content = msg_last.alarm_content
        tim_last = (datetime.datetime.now() - msg_last.alarm_time).seconds / 60
    else:
        msg_num = 0
        msg_last_content = ''
        tim_last = ''
    return render(request, 'oracle_mon/oracle_audit.html', {'tagsdefault': tagsdefault, 'tagsinfo':tagsinfo, 'msg_num':msg_num, 'msg_last_content':msg_last_content, 'tim_last':tim_last, 'audit_contents':audit_contents, 'owner':owner, 'object':object})


def oracle_ctl(request):
    # 告警
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    oper_type = request.GET.get('oper_type')
    host = request.GET.get('host')
    tags = request.GET.get('tags')
    message_info = request.GET.get('message_info')

    if oper_type:
        sql = '''select host,user_os,password_os,ssh_port_os,version from tab_oracle_servers where tags='%s' ''' % tags
        oracle = tools.mysql_query(sql)
        host = oracle[0][0]
        user = oracle[0][1]
        password = oracle[0][2]
        password = base64.decodestring(password)
        ssh_port = oracle[0][3]
        version = oracle[0][4]

        if oper_type == 'startup':
            task.oracle_startup.delay(tags,host, user, password,ssh_port,version)
            messages.add_message(request,messages.INFO,'正在启动' )

        elif oper_type == 'shutdown':
            task.oracle_shutdown.delay(tags,host, user, password,ssh_port,version)
            messages.add_message(request,messages.INFO,'正在关闭')
        else:
            task.oracle_restart.delay(tags, host, user, password,ssh_port,version)
            message_info = '正在重启'
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
    return render(request, 'oracle_mon/oracle_ctl.html',
                  {'messageinfo_list': messageinfo_list, 'oracle_ctls': oracle_ctls,
                               'msg_num': msg_num, 'now': now,
                               'msg_last_content': msg_last_content, 'tim_last': tim_last}
                  )

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
    return render(request, 'oracle_mon/sql_exec.html',
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
def get_oracle_log(request):

    tags = request.GET.get('tags')

    sql = '''select host,port,service_name,user,password,user_os,password_os,ssh_port_os,logfile from tab_oracle_servers where tags='%s' ''' % tags
    oracleinfo = tools.mysql_query(sql)
    host,port,service_name,user,password,user_os,password_os,ssh_port_os,logfile = oracleinfo[0]
    password = base64.decodestring(password)
    password_os = base64.decodestring(password_os)
    if not logfile:
        # 后台日志参数
        url = host + ':' + port + '/' + service_name
        conn = cx_Oracle.connect(user, password, url)
        cur = conn.cursor()
        sql = "select value from v$diag_info where name = 'Diag Trace'"
        cur.execute(sql)
        # 后台日志路径
        log_path, = cur.fetchone()
        logfile = '%s/alert_*.log' %log_path

    # ssh到主机获取日志内容
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(host, ssh_port_os, user_os, password_os)
    cmd = 'tail -300 %s' %logfile
    std_in, std_out, std_err = ssh_client.exec_command(cmd)
    log = std_out.read()

    return render_to_response('frame/show_log.html',
                              {'tags':tags,'log':log})